from typing import Any, Dict, List

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bson import ObjectId
from datetime import datetime
import logging

from pymongo.results import UpdateResult

from app.bot.keyboards import main_menu, recurring_menu, delete_menu
from app.dependencies.reminder_dependencies import reminder_notification



from app.core.database import get_mongo

notification_collection = get_mongo()["notifications"]


router = Router()


logger: logging.Logger = logging.getLogger(name="app_logger")  # <-- Получаем готовый логгер



class ReminderState(StatesGroup):
    waiting_for_text = State()
    waiting_for_date = State()
    waiting_for_recurring = State()
    waiting_for_frequency = State() 


# Создание нового напоминания
@router.message(F.text == "Создать напоминание")
async def create_reminder(message: Message, state: FSMContext) -> None:
    logger.info(f" Пользователь {message.from_user.id} начал создание напоминания")
    await message.answer("Введите текст напоминания:")
    await state.set_state(ReminderState.waiting_for_text)


@router.message(ReminderState.waiting_for_text)
async def get_reminder_text(message: Message, state: FSMContext) -> None:
    logger.info(f"Пользователь {message.from_user.id} ввел текст напоминания: {message.text}")
    await state.update_data(text=message.text)
    await message.answer("Введите дату напоминания в формате: YYYY-MM-DD HH:MM")
    await state.set_state(ReminderState.waiting_for_date)


@router.message(ReminderState.waiting_for_date)
async def get_reminder_date(message: Message, state: FSMContext) -> None:
    data: Dict[str, Any] = await state.get_data()
    try:
        reminder_date: datetime = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(date=reminder_date)
        logger.info(msg=f" Пользователь {message.from_user.id} выбрал дату: {reminder_date}")
        await message.answer(text="Напоминание должно повторяться? (Да/Нет)")
        await state.set_state(state=ReminderState.waiting_for_recurring)
    except ValueError:
        logger.warning(msg=f"Пользователь {message.from_user.id} ввел неверный формат даты: {message.text}")
        await message.answer(text="❌ Ошибка! Неверный формат даты. Попробуйте снова (YYYY-MM-DD HH:MM).")


@router.message(ReminderState.waiting_for_recurring)
async def get_recurring(message: Message, state: FSMContext) -> None:
    data: Dict[str, Any] = await state.get_data()

    if message.text.lower() == "да":
        await message.answer(text="Выберите частоту: Ежедневные, Еженедельные, Ежемесячные", reply_markup=recurring_menu)
        await state.set_state(state=ReminderState.waiting_for_frequency)  # Переход в новый шаг
    elif message.text.lower() == "нет":
        await reminder_notification.add_reminder(
            user_id=str(message.from_user.id),
            message=data["text"],
            date=data["date"],
            recurring=None  
        )
        logger.info(msg=f"Пользователь {message.from_user.id} создал разовое напоминание: {data['text']}")
        await message.answer(text="✅ Напоминание успешно создано!")
        await state.clear()
    else:
        logger.warning(msg=f"Пользователь {message.from_user.id} ввел неверный ответ: {message.text}")
        await message.answer(text="❌ Ошибка! Введите 'Да' или 'Нет'.")


@router.message(ReminderState.waiting_for_frequency)
async def get_recurring_frequency(message: Message, state: FSMContext) -> None:
    data: Dict[str, Any] = await state.get_data()
    recurring_mapping: dict[str, str] = {
        "Ежедневные": "daily",
        "Еженедельные": "weekly",
        "Ежемесячные": "monthly"
    }

    recurring: str | None = recurring_mapping.get(message.text)  # Сопоставляем с доступными вариантами

    if not recurring:
        logger.warning(msg=f"Пользователь {message.from_user.id} выбрал некорректную частоту: {message.text}")
        await message.answer(text="❌ Ошибка! Выберите одну из опций: 'Ежедневные', 'Еженедельные', 'Ежемесячные'.")
        return

    # Добавление напоминания с повторением
    await reminder_notification.add_reminder(
        user_id=str(object=message.from_user.id),
        message=data["text"],
        date=data["date"],
        recurring=recurring
    )
    logger.info(f"Пользователь {message.from_user.id} создал повторяющееся напоминание: {data['text']}, Частота: {message.text}")
    await message.answer(f"✅ Напоминание успешно создано! Будет повторяться {message.text}.")
    await state.clear()


# Просмотр всех активных напоминаний
@router.message(F.text == "Список напоминаний")
async def view_reminders(message: Message):
    try:
        reminders: List[Dict[str, Any]] = await reminder_notification.get_all_reminders(user_id=str(message.from_user.id))

        # Сопоставление системных имен с удобными для пользователя
        recurring_mapping: Dict[str, str] = {
            "daily": "Ежедневные",
            "weekly": "Еженедельные",
            "monthly": "Ежемесячные"
        }

        if reminders:
            response: str = "\n\n".join(
                f"📌 {r['message']} | 🕒 {r['date']} | 🔁 {recurring_mapping.get(r['recurring'], 'Однократно')}"
                for r in reminders
            )
        else:
            response = "Нет активных напоминаний."

        logger.info(msg=f"Пользователь {message.from_user.id} запросил список напоминаний ({len(reminders)} шт.)")
        await message.answer(text=response)
    except Exception as e:
        logger.error(msg=f"Ошибка при загрузке напоминаний пользователя {message.from_user.id}: {e}")
        await message.answer(text=f"Ошибка при загрузке напоминаний: {e}")


# Удаление напоминаний
@router.message(F.text == "Удалить напоминание")
async def delete_reminder_prompt(message: Message) -> None:
    try:
        reminders: List[Dict[str, Any]] = await reminder_notification.get_all_reminders(user_id=str(message.from_user.id))
        if reminders:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{r['message']} | {r['date']}",
                        callback_data=f"delete_reminder:{r['_id']}"
                    )
                ]
                for r in reminders
            ])
            await message.answer(text="Выберите напоминание для удаления:", reply_markup=keyboard)
        else:
            await message.answer(text="Нет активных напоминаний.")
    except Exception as e:
        logger.error(msg=f"Ошибка при загрузке напоминаний для удаления (пользователь {message.from_user.id}): {e}")
        await message.answer(text=f"Ошибка при загрузке напоминаний: {e}")


@router.callback_query(F.data.startswith("delete_reminder:"))
async def delete_reminder_callback(callback_query: CallbackQuery) -> None:
    reminder_id: str = callback_query.data.split(sep=":")[1]
    try:
        result: bool = await reminder_notification.remove_reminder(user_id=str(object=callback_query.from_user.id), reminder_id=reminder_id)
        if result:
            logger.info(msg=f"Пользователь {callback_query.from_user.id} удалил напоминание {reminder_id}")
            await callback_query.message.edit_text("✅ Напоминание успешно удалено.")
        else:
            logger.warning(msg=f"Пользователь {callback_query.from_user.id} пытался удалить несуществующее напоминание {reminder_id}")
            await callback_query.message.edit_text("❌ Напоминание не найдено.")
    except Exception as e:
        logger.error(msg=f"Ошибка при удалении напоминания {reminder_id} пользователем {callback_query.from_user.id}: {e}")
        await callback_query.message.edit_text(f"Ошибка при удалении напоминания: {e}")





@router.callback_query(F.data.startswith("confirm_reminder:"))
async def confirm_reminder(callback_query: CallbackQuery) -> None:
    """Обрабатывает подтверждение напоминания пользователем."""
    reminder_id: str = callback_query.data.split(sep=":")[1]

    result: UpdateResult = await notification_collection.update_one(
        filter={"_id": ObjectId(reminder_id)},
        update={"$set": {"completed": True}}
    )

    if result.modified_count > 0:
        logger.info(msg=f"✅ Пользователь {callback_query.from_user.id} подтвердил напоминание {reminder_id}")
        await callback_query.message.edit_text("✅ Напоминание подтверждено.")
    else:
        await callback_query.answer(text="❌ Ошибка: напоминание уже подтверждено или не найдено.", show_alert=True)
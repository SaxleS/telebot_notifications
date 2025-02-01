import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.keyboards import main_menu, settings_menu, timezone_menu
from app.repositories.users_repository import user_service

router = Router()
logger: logging.Logger = logging.getLogger(name="app_logger")

class UserState(StatesGroup):
    waiting_for_timezone = State()


@router.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name or "Неизвестно"


    # Проверяем, есть ли пользователь в базе
    user = await user_service.get_user(user_id=user_id)
    
    if not user:
        # Если пользователя нет
        await message.answer(
            "Добро пожаловать! 🚀\n"
            "Пожалуйста, выберите ваш часовой пояс:",
            reply_markup=timezone_menu
        )
        await state.set_state(state=UserState.waiting_for_timezone)
    else:
        await message.answer(text=f"С возвращением, {first_name}!", reply_markup=main_menu)


@router.message(UserState.waiting_for_timezone)
async def set_timezone(message: Message, state: FSMContext):
    user_id = str(object=message.from_user.id)
    timezone = message.text  # Получаем выбранный пользователем часовой пояс

    # Сохраняем пользователя в базе
    await user_service.register_or_update_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        timezone=timezone,
    )

    await message.answer(text="✅ Часовой пояс установлен! Теперь можно использовать бота.", reply_markup=main_menu)
    await state.clear()


@router.message(F.text == "Настройки профиля")
async def open_settings(message: Message):
    await message.answer(text="🔧 Настройки профиля:", reply_markup=settings_menu)


@router.message(F.text == "Установить часовой пояс")
async def change_timezone(message: Message, state: FSMContext) -> None:
    await message.answer(text="Выберите ваш новый часовой пояс:", reply_markup=timezone_menu)
    await state.set_state(state=UserState.waiting_for_timezone)


@router.message(F.text == "Назад в главное меню")
async def back_to_main(message: Message, state: FSMContext) -> None:
    await message.answer("🔙 Возвращаемся в главное меню", reply_markup=main_menu)
    await state.clear()
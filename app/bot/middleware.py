import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List
import pytz
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.dependencies.reminder_dependencies import reminder_middleware_notification

logger: logging.Logger = logging.getLogger(name="app_logger")


class ReminderNotifier:
    """Middleware для отправки уведомлений пользователям с возможностью подтверждения."""

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.is_running = True

    async def start(self) -> None:
        """Запускает цикл проверки напоминаний."""
        while self.is_running:
            try:
                await self.check_reminders()
            except Exception as e:
                logger.error(msg=f"Ошибка в обработке уведомлений: {e}")

            await asyncio.sleep(delay=60)  # Проверяем раз в минуту

    async def check_reminders(self) -> None:
            """Проверяет, есть ли напоминания, которые нужно отправить."""
            now: datetime = datetime.now()  # Локальное время сервера

            reminders: List[Dict[str, Any]] = await reminder_middleware_notification.get_all_active_reminders()  # Получаем ВСЕ активные напоминания

            for reminder in reminders:
                user_id = reminder["user_id"]
                reminder_time = reminder["date"]
                reminder_id = str(object=reminder["_id"])
                recurring = reminder.get("recurring", None)

                # Получаем часовой пояс пользователя через сервис
                user_timezone: str = await reminder_middleware_notification.get_user_timezone(user_id=user_id)
                user_tz: pytz._UTCclass | pytz.StaticTzInfo | pytz.DstTzInfo = pytz.timezone(user_timezone)

                # Преобразуем `naive` datetime в `aware`, если необходимо
                if reminder_time.tzinfo is None:
                    reminder_time = user_tz.localize(reminder_time)

                now_local: datetime = now.astimezone(user_tz)

                # Проверяем отправку уведомления
                if now_local >= reminder_time:
                    if recurring:
                        await self.bot.send_message(chat_id=user_id, text=f"🔔 Напоминание: {reminder['message']}")
                        logger.info(msg=f"Повторяющееся напоминание {reminder_id} отправлено пользователю {user_id}")

                        # Переносим напоминание на следующую дату без изменения времени
                        await reminder_middleware_notification.move_to_next_occurrence(reminder_id=reminder_id, recurring=recurring)
                    else:
                        confirm_button = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_reminder:{reminder_id}")]
                        ])
                        await self.bot.send_message(chat_id=user_id, text=f"🔔 Напоминание: {reminder['message']}", reply_markup=confirm_button)
                        logger.info(msg=f"Разовое напоминание {reminder_id} отправлено пользователю {user_id}")

                        # Ждем 5 минут, если не подтверждено → завершаем
                        await asyncio.sleep(delay=300)
                        await self.mark_as_completed(reminder_id=reminder_id, recurring=recurring)

    async def mark_as_completed(self, reminder_id: str, recurring: str) -> None:
        """Отмечает разовое напоминание как выполненное."""
        if not recurring:
            await reminder_middleware_notification.mark_reminder_completed(reminder_id)
            logger.info(msg=f"Напоминание {reminder_id} автоматически подтверждено (тайм-аут).")

    async def handle_confirmation(self, callback_query: CallbackQuery) -> None:
        """Обрабатывает нажатие на кнопку 'Подтвердить'."""
        reminder_id: str = callback_query.data.split(sep=":")[1]

        reminder = await reminder_middleware_notification.get_reminder_by_id(reminder_id)

        if not reminder:
            await callback_query.answer(text="❌ Напоминание не найдено.", show_alert=True)
            return

        recurring = reminder.get("recurring", None)

        await self.mark_as_completed(reminder_id=reminder_id, recurring=recurring)

        await callback_query.message.edit_text("✅ Напоминание выполнено.")
        await callback_query.answer(text="Напоминание отмечено как выполненное!", show_alert=True)
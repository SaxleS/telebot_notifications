from logging import Logger
from aiogram import Bot, Dispatcher
import asyncio
from app.core.logger import Logger
from app.bot.handlers import start, reminders, help
from app.bot.middleware import ReminderNotifier
from app.core.config import Settings, get_settings

settings: Settings = get_settings()


logger: Logger = Logger.setup_logger()

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
reminder_notifier = ReminderNotifier(bot=bot)

# Подключаем хэндлеры
dp.include_router(start.router)
dp.include_router(reminders.router)
dp.include_router(help.router)

async def run_bot():
    logger.info("🚀 Запуск бота...")
    
    # Запускаем напоминания в фоне
    asyncio.create_task(coro=reminder_notifier.start())

    await dp.start_polling(bot)

def main() -> None:
    asyncio.run(main=run_bot())

if __name__ == "__main__":
    main()
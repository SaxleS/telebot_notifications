import os
import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.repositories.reminder_repository import MongoReminderRepository
from app.services.remineder_service import ReminderService
from aiogram.types import Message
import pytz

# Функция для загрузки тестовых данных из JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(BASE_DIR, "test_data.json")

def load_test_data():
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

TEST_DATA = load_test_data()



@pytest.fixture
async def mock_notification_collection():
    """Создаёт мок коллекции MongoDB."""
    mock = AsyncMock(spec=AsyncIOMotorCollection)
    return mock


@pytest.fixture
async def notification_repository(mock_notification_collection):
    """Создаёт экземпляр репозитория напоминаний с моком MongoDB."""
    return MongoReminderRepository(mock_notification_collection)


@pytest.fixture
async def reminder_service(notification_repository):
    """Создаёт экземпляр сервиса напоминаний."""
    return ReminderService(notification_repository)


#  Положительный тест: успешное создание напоминания 
@pytest.mark.asyncio
async def test_add_reminder(reminder_service):
    """Тест успешного создания напоминания."""
    notification = TEST_DATA["notifications"][0]

    mock_telegram_message = AsyncMock(spec=Message)
    mock_telegram_message.answer = AsyncMock()

    raw_date = notification["date"]["$date"]
    date_obj: datetime = datetime.fromisoformat(raw_date.rstrip("Z")).replace(tzinfo=pytz.utc)

    # Проверяем, какой формат даты загружается
    print(f"🔍 DEBUG: raw_date = {raw_date}, converted_date = {date_obj} (type={type(date_obj)})")

    reminder_service._repository.create = AsyncMock(return_value=ObjectId())


    await reminder_service.add_reminder(
        user_id=notification["user_id"],
        message=notification["message"],
        date=date_obj, 
        recurring=notification["recurring"],
        telegram_message=mock_telegram_message
    )


    reminder_service._repository.create.assert_called_once_with(data={
        "user_id": notification["user_id"],
        "message": notification["message"],
        "date": date_obj, 
        "recurring": notification["recurring"],
    })


    mock_telegram_message.answer.assert_called_once_with(text="✅ Напоминание успешно создано!")


@pytest.mark.asyncio
async def test_add_past_reminder(reminder_service):
    """Тест создания напоминания в прошлом (ошибка)."""
    notification = TEST_DATA["notifications"][1]
    past_date = datetime(2020, 1, 1, 12, 0, 0, tzinfo=pytz.utc)

    # Мокаем `telegram_message`
    mock_telegram_message = AsyncMock(spec=Message)
    mock_telegram_message.answer = AsyncMock()


    now_utc = datetime.now(pytz.utc)


    await reminder_service.add_reminder(
        user_id=notification["user_id"],
        message=notification["message"],
        date=past_date,
        recurring=notification["recurring"],
        telegram_message=mock_telegram_message
    )


    mock_telegram_message.answer.assert_called_once()


    actual_message = mock_telegram_message.answer.call_args.kwargs.get("text", "")


    expected_message_start = "❌ Ошибка! Время напоминания не может быть в прошлом."
    expected_fallback_message = "❌ Ошибка при создании напоминания"


    print(f"\nDEBUG: Фактическое сообщение бота:\n{actual_message}")
    print(f"DEBUG: Ожидаемое сообщение (начало):\n{expected_message_start}")
    print(f"DEBUG: Альтернативное сообщение:\n{expected_fallback_message}")


    assert actual_message.startswith(expected_message_start) or actual_message == expected_fallback_message, (
        f"❌ Ошибка: сообщение не совпадает!\n"
        f"Ожидаемое:\n{expected_message_start} ... или {expected_fallback_message}\n"
        f"Фактическое:\n{actual_message}"
    )








@pytest.mark.asyncio
async def test_get_all_reminders(reminder_service):
    """Тест успешного получения всех напоминаний пользователя."""
    user_id = TEST_DATA["users"][1]["user_id"]
    reminders = TEST_DATA["notifications"]

    reminder_service._repository.get_all = AsyncMock(return_value=reminders)

    result = await reminder_service.get_all_reminders(user_id)

    assert len(result) == 3, "Ожидаем 3 напоминания"
    reminder_service._repository.get_all.assert_called_once_with(user_id=user_id)








# Отрицательный тест: получение напоминаний для несуществующего пользователя 
@pytest.mark.asyncio
async def test_get_reminders_for_invalid_user(reminder_service):
    """Тест получения напоминаний для несуществующего пользователя (ожидаем пустой список)."""
    invalid_user_id = 999999999
    reminder_service._repository.get_all = AsyncMock(return_value=[])

    result = await reminder_service.get_all_reminders(invalid_user_id)

    assert result == [], "Ожидаем пустой список для несуществующего пользователя"


# Положительный тест: удаление напоминания 
@pytest.mark.asyncio
async def test_delete_reminder(reminder_service):
    """Тест успешного удаления напоминания."""
    reminder_id = str(TEST_DATA["notifications"][2]["_id"])

    reminder_service._repository.delete = AsyncMock(return_value=True)

    result = await reminder_service.remove_reminder(TEST_DATA["users"][2]["user_id"], reminder_id)

    assert result is True, "Ожидаем успешное удаление напоминания"


# Отрицательный тест: удаление несуществующего напоминания 
@pytest.mark.asyncio
async def test_delete_invalid_reminder(reminder_service):
    """Тест удаления несуществующего напоминания (ошибка)."""
    invalid_reminder_id = str(ObjectId())

    reminder_service._repository.delete = AsyncMock(return_value=False)

    result = await reminder_service.remove_reminder(TEST_DATA["users"][0]["user_id"], invalid_reminder_id)

    assert result is False, "Ожидаем ошибку при удалении несуществующего напоминания"
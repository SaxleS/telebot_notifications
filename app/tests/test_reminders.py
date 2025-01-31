import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_create_reminder(reminder_service):
    """Тест создания напоминания через сервис."""
    user_id = "test_user"
    message = "Test reminder"
    date = datetime.utcnow()

    reminder_id = await reminder_service.add_reminder(
        user_id=user_id,
        message=message,
        date=date
    )
    assert reminder_id is not None, "Ожидаем, что напоминание будет создано"

@pytest.mark.asyncio
async def test_get_all_reminders(reminder_service):
    """Тест получения всех напоминаний пользователя."""
    user_id = "test_user"
    
    # Добавляем 2 напоминания
    await reminder_service.add_reminder(user_id, "Reminder 1", datetime.utcnow())
    await reminder_service.add_reminder(user_id, "Reminder 2", datetime.utcnow())

    reminders = await reminder_service.get_all_reminders(user_id)
    assert len(reminders) == 2, "Ожидаем, что у пользователя 2 напоминания"

@pytest.mark.asyncio
async def test_mark_reminder_completed(reminder_service):
    """Тест завершения напоминания."""
    user_id = "test_user"
    reminder_id = await reminder_service.add_reminder(
        user_id, "Complete me!", datetime.utcnow()
    )

    result = await reminder_service.mark_reminder_completed(user_id, reminder_id)
    assert result is True, "Напоминание должно быть помечено выполненным"

@pytest.mark.asyncio
async def test_delete_reminder(reminder_service):
    """Тест удаления напоминания."""
    user_id = "test_user"
    reminder_id = await reminder_service.add_reminder(
        user_id, "Delete me!", datetime.utcnow()
    )

    deleted = await reminder_service.remove_reminder(user_id, reminder_id)
    assert deleted is True, "Напоминание должно быть удалено"
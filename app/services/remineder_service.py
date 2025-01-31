from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import UpdateResult

import logging
from bson import ObjectId

from app.crud.reminder_crud import IReminderRepository, MongoReminderRepository


from app.core.database import get_mongo

users_collection = get_mongo()["users"]


class ReminderService:
    """Сервис для управления напоминаниями."""
    
    def __init__(self, repository: IReminderRepository) -> None:
        self._repository: IReminderRepository = repository
    
    async def add_reminder(self, user_id: str, message: str, date: datetime, recurring: Optional[str] = None) -> Any:
        reminder_data = {
            "user_id": user_id,
            "message": message,
            "date": date,
            "recurring": recurring
        }
        return await self._repository.create(data=reminder_data)
    
    async def get_all_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        return await self._repository.get_all(user_id=user_id)
    
    async def mark_reminder_completed(self, user_id: str, reminder_id: str) -> bool:
        return await self._repository.mark_completed(user_id=user_id, reminder_id=reminder_id)

    async def remove_reminder(self, user_id: str, reminder_id: str) -> bool:
        return await self._repository.delete(user_id=user_id, reminder_id=reminder_id)
    




class ReminderServiceNotificationMiddleware(ReminderService):
    """Расширенный сервис для управления напоминаниями."""

    def __init__(self, repository: MongoReminderRepository) -> None:
        super().__init__(repository)

    async def get_all_active_reminders(self) -> List[Dict[str, Any]]:
        """Получает ВСЕ активные напоминания (не завершенные)."""
        return await self._repository._collection.find({"completed": False}).to_list(None)

    async def move_to_next_occurrence(self, reminder_id: str, recurring: str) -> bool:
        """Переносит повторяющееся напоминание на следующую дату без изменения времени."""
        reminder = await self._repository._collection.find_one({"_id": ObjectId(oid=reminder_id)})

        if not reminder or "date" not in reminder:
            return False  # Если напоминание не найдено, выходим

        current_date = reminder["date"]

        if recurring == "daily":
            new_date = current_date + timedelta(days=1)
        elif recurring == "weekly":
            new_date = current_date + timedelta(weeks=1)
        elif recurring == "monthly":
            new_date = current_date + timedelta(weeks=4)
        else:
            return False

        await self._repository._collection.update_one(
            {"_id": ObjectId(reminder_id)},
            {"$set": {"date": new_date}}
        )
        return True
    
    async def get_user_timezone(self, user_id: str) -> str:
        """Получает часовой пояс пользователя из базы данных."""
        user = await users_collection.find_one(filter={"user_id": user_id})
        return user["timezone"] if user else "UTC"

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import UpdateResult

import logging
from bson import ObjectId


from app.core.database import get_mongo

notification_collection = get_mongo()["notifications"]


class IReminderRepository(ABC):
    """Интерфейс для работы с напоминаниями в базе данных."""
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Any:
        pass
    
    @abstractmethod
    async def get_all(self, user_id: str) -> List[Dict[str, Any]]:
        """Получает все напоминания конкретного пользователя."""
        pass
    
    @abstractmethod
    async def mark_completed(self, user_id: str, reminder_id: str) -> bool:
        """Отмечает разовое напоминание как выполненное для конкретного пользователя."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str, reminder_id: str) -> bool:
        pass


class MongoReminderRepository(IReminderRepository):
    """Реализация репозитория напоминаний на основе MongoDB."""
    
    def __init__(self, collection: AsyncIOMotorCollection)  -> None:
        self._collection = collection
    
    async def create(self, data: Dict[str, Any]) -> Any:
        logging.info(f"Попытка добавить напоминание: {data}")

        data["timestamp"] = datetime.utcnow()  # Время создания
        data["completed"] = False  # Флаг выполнения
        data["status"] = "created"  # Статус напоминания

        result = await self._collection.insert_one(data)
        logging.info(f"Напоминание добавлено с ID {result.inserted_id}")

        return str(result.inserted_id)
    
    async def get_all(self, user_id: str) -> List[Dict[str, Any]]:
        """Возвращает только напоминания конкретного пользователя."""
        return await self._collection.find({"user_id": user_id, "completed": False}).to_list(None)
    
    async def mark_completed(self, user_id: str, reminder_id: str) -> bool:
        """Помечает разовое напоминание как выполненное и обновляет повторяющиеся."""
        reminder = await self._collection.find_one(filter={"_id": ObjectId(oid=reminder_id), "user_id": user_id})
        if not reminder:
            return False
        
        if reminder["recurring"]:  # Если напоминание повторяется
            new_date = reminder["date"]

            if reminder["recurring"] == "daily":
                new_date += timedelta(days=1)
            elif reminder["recurring"] == "weekly":
                new_date += timedelta(weeks=1)
            elif reminder["recurring"] == "monthly":
                new_date += timedelta(weeks=4)

            await self._collection.update_one(
                filter={"_id": ObjectId(oid=reminder_id), "user_id": user_id},
                update={"$set": {"date": new_date}}
            )
            return True
        else:  # Разовое напоминание
            result: UpdateResult = await self._collection.update_one(
                filter={"_id": ObjectId(reminder_id), "user_id": user_id},
                update={"$set": {"completed": True}}
            )
            return result.modified_count > 0
    
    async def delete(self, user_id: str, reminder_id: str) -> bool:
        """Удаляет напоминание конкретного пользователя."""
        result = await self._collection.delete_one(filter={"_id": ObjectId(reminder_id), "user_id": user_id})
        if result.deleted_count > 0:
            await notification_collection.insert_one(document={
                "user_id": user_id,
                "status": "deleted",
                "timestamp": datetime.utcnow()
            })
        return result.deleted_count > 0

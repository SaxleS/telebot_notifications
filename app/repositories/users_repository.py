from datetime import datetime
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorCollection
from abc import ABC, abstractmethod


from app.core.mongo_collections import users_collection






class IUserRepository(ABC):
    """Интерфейс для работы с пользователями в MongoDB."""

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Получает данные пользователя по его Telegram ID."""
        pass

    @abstractmethod
    async def create_or_update_user(self, user_id: str, username: str, first_name: str, last_name: str, timezone: str):
        """Создает нового пользователя или обновляет существующего."""
        pass

    @abstractmethod
    async def update_timezone(self, user_id: str, timezone: str):
        """Обновляет часовой пояс пользователя."""
        pass


class MongoUserRepository(IUserRepository):
    """Реализация репозитория пользователей на MongoDB."""

    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    async def get_user(self, user_id: str) -> Optional[Dict]:
        return await self._collection.find_one({"user_id": user_id})

    async def create_or_update_user(self, user_id: str, username: str, first_name: str, last_name: str, timezone: str):
        user_data = {
            "user_id": user_id,
            "username": username or "Неизвестный",
            "first_name": first_name or "Неизвестно",
            "last_name": last_name or "Неизвестно",
            "timezone": timezone,
            "registered_at": datetime.utcnow(),
        }

        await self._collection.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )

    async def update_timezone(self, user_id: str, timezone: str):
        await self._collection.update_one(
            {"user_id": user_id},
            {"$set": {"timezone": timezone}}
        )


class UserService:
    """Сервис для работы с пользователями. Использует абстрактный репозиторий."""

    def __init__(self, repository: IUserRepository):
        self._repository = repository

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Получает пользователя через репозиторий."""
        return await self._repository.get_user(user_id)

    async def register_or_update_user(self, user_id: str, username: str, first_name: str, last_name: str, timezone: str):
        """Создает или обновляет пользователя через репозиторий."""
        await self._repository.create_or_update_user(user_id, username, first_name, last_name, timezone)

    async def set_user_timezone(self, user_id: str, timezone: str):
        """Обновляет часовой пояс пользователя."""
        await self._repository.update_timezone(user_id, timezone)


# Инициализация репозитория и сервиса пользователей
user_repository = MongoUserRepository(users_collection)
user_service = UserService(user_repository)
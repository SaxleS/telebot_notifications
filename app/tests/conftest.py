import os
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from app.crud.reminder_crud import MongoReminderRepository
from app.services.remineder_service import ReminderService

from app.core.config import get_settings



settings = get_settings()



@pytest.fixture(scope="function")
async def test_db():
    client = AsyncIOMotorClient(settings.get_mongo_url())
    db = client[settings.get_database_name()]
    yield db
    await client.drop_database(settings.get_database_name())
    client.close()

@pytest.fixture(scope="function")
async def reminder_repository(test_db):
    repo = MongoReminderRepository(
        test_db[settings.get_notifications_collection()]
    )
    await test_db[settings.get_notifications_collection()].delete_many({})
    return repo

@pytest.fixture(scope="function")
async def reminder_service(reminder_repository):
    return ReminderService(repository=reminder_repository)
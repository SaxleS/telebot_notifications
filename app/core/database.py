from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import Settings, get_settings






def get_mongo():
    """Создаёт новое подключение к MongoDB с актуальными настройками."""
    settings: Settings = get_settings()  # Теперь TESTING всегда актуален
    mongo_client = AsyncIOMotorClient(host=settings.get_mongo_url())
    mongo_database = mongo_client[settings.get_database_name()]
    
    return {
        "client": mongo_client,
        "database": mongo_database,
        "notifications": mongo_database[settings.get_notifications_collection()],
        "logs": mongo_database[settings.get_users_collection()],
        "users": mongo_database[settings.get_users_collection()],
    }





# mongo_client = AsyncIOMotorClient(host=settings.MONGO_URL)
# mongo_database = mongo_client[settings.MONGO_DATABASE_NAME]


# notification_collection = mongo_database[settings.MONGO_NOTIFICATIONS_COLLECTION]
# logs_collection = mongo_database[settings.MONGO_LOGS_COLLECTION]
# users_collection = mongo_database[settings.MONGO_USERS_COLLECTION]
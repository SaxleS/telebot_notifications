from app.core.database import get_mongo

notification_collection = get_mongo()["notifications"]
users_collection = get_mongo()["users"]
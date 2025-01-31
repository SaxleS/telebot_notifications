




from app.crud.reminder_crud import MongoReminderRepository

from app.services.remineder_service import ReminderService, ReminderServiceNotificationMiddleware


from app.core.database import get_mongo

notification_collection = get_mongo()["notifications"]



reminder_middleware_notification = ReminderServiceNotificationMiddleware(repository=MongoReminderRepository(collection=notification_collection))
reminder_notification = ReminderService(repository=MongoReminderRepository(collection=notification_collection))
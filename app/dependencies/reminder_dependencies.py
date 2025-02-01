




from app.repositories.reminder_repository import MongoReminderRepository

from app.services.remineder_service import ReminderService, ReminderServiceNotificationMiddleware


from app.core.mongo_collections import notification_collection






reminder_middleware_notification = ReminderServiceNotificationMiddleware(repository=MongoReminderRepository(collection=notification_collection))
reminder_notification = ReminderService(repository=MongoReminderRepository(collection=notification_collection))
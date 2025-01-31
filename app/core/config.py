import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    MONGO_URL: str
    MONGO_DATABASE_NAME: str
    MONGO_NOTIFICATIONS_COLLECTION: str
    MONGO_USERS_COLLECTION: str
    MONGO_LOGS_COLLECTION: str
    BOT_TIMEZONE: str = "UTC"

    # Флаг тестирования (устанавливается через переменные окружения)
    TESTING: bool = os.getenv("TESTING", "False") == "True"

    TEST_MONGO_URL: str
    TEST_DB_NAME: str
    TEST_MONGO_NOTIFICATIONS_COLLECTION: str
    TEST_MONGO_USERS_COLLECTION: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_mongo_url(self) -> str:
        return self.TEST_MONGO_URL if self.TESTING else self.MONGO_URL

    def get_database_name(self) -> str:
        return self.TEST_DB_NAME if self.TESTING else self.MONGO_DATABASE_NAME

    def get_notifications_collection(self) -> str:
        return self.TEST_MONGO_NOTIFICATIONS_COLLECTION if self.TESTING else self.MONGO_NOTIFICATIONS_COLLECTION

    def get_users_collection(self) -> str:
        return self.TEST_MONGO_USERS_COLLECTION if self.TESTING else self.MONGO_USERS_COLLECTION


def get_settings() -> Settings:
    """Создаёт новый экземпляр конфигурации при каждом вызове."""
    return Settings()
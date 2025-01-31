from pydantic import BaseModel, Field
from datetime import datetime


class LogEntry(BaseModel):
    level: str = Field(..., description="Уровень логирования (INFO, ERROR и т.д.)")
    message: str = Field(..., description="Сообщение лога")
    module: str = Field(None, description="Модуль, откуда пришел лог")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время записи")
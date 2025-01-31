import logging
import queue
import threading
from datetime import datetime

from pymongo import MongoClient

from app.core.config import Settings, get_settings

settings: Settings = get_settings()


class ThreadedMongoLogHandler(logging.Handler):
    """
    Логгер, который записывает логи в MongoDB в отдельном потоке.
    """

    def __init__(self):
        super().__init__()
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Подключаемся к MongoDB через PyMongo (синхронно)
        self.client = MongoClient(settings.MONGO_URL)
        db = self.client[settings.MONGO_DATABASE_NAME]
        # Если нужно взять имя коллекции из .env: settings.MONGO_LOGS_COLLECTION
        self.collection = db[settings.MONGO_LOGS_COLLECTION]

        # Запускаем поток, который будет забирать логи из очереди
        self.worker = threading.Thread(
            target=self._log_consumer, 
            name="MongoLogWorker", 
            daemon=True
        )
        self.worker.start()
        print("ThreadedMongoLogHandler инициализирован.")

    def emit(self, record: logging.LogRecord):
        """
        Кладём лог в очередь.
        """
        # Формируем документ, который отправим в Mongo
        log_document = {
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "timestamp": datetime.utcnow(),
        }
        self.log_queue.put(log_document)

    def _log_consumer(self):
        """
        Цикл, который крутится в отдельном потоке и пишет логи в MongoDB.
        """
        while not self.stop_event.is_set():
            try:
                log_document = self.log_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                result = self.collection.insert_one(log_document)
                # Можно вывести в консоль
                print(f"Лог записан в MongoDB с ID {result.inserted_id}")
            except Exception as e:
                print(f"❌ Ошибка записи лога в MongoDB: {e}")

    def close(self):
        """
        Останавливаем поток и закрываем соединение с MongoDB.
        """
        self.stop_event.set()
        self.worker.join(timeout=2)
        self.client.close()
        super().close()

class Logger:
    """
    Класс-обёртка для доступа к нашему поточному MongoDB-логгеру.
    """

    @staticmethod
    def setup_logger():
        print("Вызов Logger.setup_logger()")  
        logger = logging.getLogger("app_logger")
        if not logger.hasHandlers():
            log_handler = ThreadedMongoLogHandler()
            logger.setLevel(logging.INFO)
            logger.addHandler(log_handler)
            print("Логгер успешно инициализирован!")
            logger.info("Логгер (Threaded) MongoDB успешно запущен.")
        return logger
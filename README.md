# 📌 Telebot Notifications

## 📝 Описание
 Telebot Notifications  — это Telegram-бот для управления напоминаниями. Бот позволяет пользователям:
- Создавать напоминания 📆
- Просматривать список активных напоминаний 📋
- Отмечать напоминания выполненными ✅
- Удалять напоминания ❌

Бот использует базу данных  MongoDB  для хранения напоминаний и настроек пользователей.

---


## 🚀 Используемые технологии
### 📌 Стек проекта:
-  Aiogram 3  — асинхронная библиотека для работы с Telegram API
-  Motor (MongoDB)  — позволяет асинхронно работать с БД.
-  Poetry  — менеджер зависимостями его имее
-  Docker + Docker Compose  — удобного деплоя изолированной среде.
-  Отделение логики на слои  — код структурирован по слоям (`bot`, `services`, `core`, `crud`), что упрощения поддержкии



---





## 🚀 Запуск локально (без Docker)
### 🔧 1. Установка зависимостей
Убедитесь, что у вас установлен  Poetry . Если нет, установите его:
```sh
pip install poetry
```

Склонируйте репозиторий и установите зависимости:
```sh
git clone https://github.com/your-repo/telebot-notifications.git
cd telebot-notifications
poetry install
```

### ⚙️ 2. Настройка `.env`
Создайте файл `.env` (или используйте `env.example`):
```sh
cp env.example .env
```
Отредактируйте `.env`, указав ваш `BOT_TOKEN` и параметры подключения к MongoDB.

### ▶️ 3. Запуск бота
```sh
poetry run python manage.py start
```

### 🧪 4. Запуск тестов
```sh
poetry run python manage.py test
```

---

## 🐳 Запуск через Docker
### 📦 1. Сборка контейнеров
```sh
docker-compose up --build -d
```


### 🔄 2. Перезапуск контейнеров
```sh
docker-compose down && docker-compose up -d
```

### 🛑 3. Остановка контейнеров
```sh
docker-compose down
```

---

## 📝 Структура проекта
```sh
telebot-notifications/
│── app/
│   ├── bot/                # Логика бота (хендлеры, middleware, keyboards)
│   ├── core/               # Основные модули (конфигурация, БД, логгер)
│   ├── crud/               # Операции с базой данных -repo
│   ├── dependencies/       # Вспомогательные зависимости
│   ├── services/           # Бизнес-логика
│   ├── tests/              # Тесты
│── docker-compose.yml      # Конфигурация Docker Compose
│── Dockerfile              # Dockerfile для сборки контейнера
│── manage.py               # Скрипт управления ботом
│── pyproject.toml          # Конфигурация Poetry
│── .env.example            # Шаблон для .env
│── README.md               # Документация проекта
```

---

## 📩 Контакты
Если у вас есть вопросы или предложения, свяжитесь со мной:
-  Telegram:  [@saxles](https://t.me/saxles)
-  Email:  aliaksei.saukin@gmail.com
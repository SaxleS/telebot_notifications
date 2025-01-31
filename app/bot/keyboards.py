from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
btn_create_reminder = KeyboardButton(text="Создать напоминание")
btn_view_reminders = KeyboardButton(text="Список напоминаний")
btn_delete_reminder = KeyboardButton(text="Удалить напоминание")
btn_settings = KeyboardButton(text="Настройки профиля")

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_create_reminder],
        [btn_view_reminders],
        [btn_delete_reminder],
        [btn_settings],
    ],
    resize_keyboard=True
)

# Подменю повторяющихся напоминаний
btn_daily = KeyboardButton(text="Ежедневные")
btn_weekly = KeyboardButton(text="Еженедельные")
btn_monthly = KeyboardButton(text="Ежемесячные")
btn_back_to_main = KeyboardButton(text="Назад в главное меню")

recurring_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_daily, btn_weekly, btn_monthly],
        [btn_back_to_main],
    ],
    resize_keyboard=True
)

# Подменю удаления напоминаний
btn_delete_specific = KeyboardButton(text="Удалить конкретное напоминание")
btn_delete_all = KeyboardButton(text="Удалить все напоминания")

delete_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_delete_specific],
        [btn_delete_all],
        [btn_back_to_main],
    ],
    resize_keyboard=True
)

# Подменю настроек пользователя
btn_set_timezone = KeyboardButton(text="Установить часовой пояс")
btn_back_to_main_settings = KeyboardButton(text="Назад в главное меню")

settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_set_timezone],
        [btn_back_to_main_settings],
    ],
    resize_keyboard=True
)

# Клавиатура с часовыми поясами (пример)
timezone_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="UTC"), KeyboardButton(text="Europe/Moscow")],
        [KeyboardButton(text="America/New_York"), KeyboardButton(text="Asia/Tokyo")],
        [btn_back_to_main],
    ],
    resize_keyboard=True
)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    keyboard = [
        [KeyboardButton(text="🏋️ Тренування"), KeyboardButton(text="📅 Історія")],
        [KeyboardButton(text="👤 Профіль"), KeyboardButton(text="🎯 Цілі")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="❓ Допомога")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
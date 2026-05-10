from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_update_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚖️ Змінити вагу", callback_data="edit_weight")],
            [InlineKeyboardButton(text="📏 Змінити зріст", callback_data="edit_height")],
            [InlineKeyboardButton(text="🎂 Змінити вік", callback_data="edit_age")],
            [InlineKeyboardButton(text="🔄 Заповнити анкету з нуля", callback_data="edit_all")]
        ]
    )


def get_done_keyboard(exercise_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Виконано",
                    callback_data=f"done_{exercise_id}"
                )
            ]
        ]
    )
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

def get_level_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Новачок",
                    callback_data="level_beginner"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔴 Досвідчений",
                    callback_data="level_advanced"
                )
            ]
        ]
    )


def get_workout_type_keyboard(level: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💪 Push",
                    callback_data=f"workout_{level}_push"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏋️ Pull",
                    callback_data=f"workout_{level}_pull"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🦵 Legs",
                    callback_data=f"workout_{level}_legs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Full Body",
                    callback_data=f"workout_{level}_fullbody"
                )
            ]
        ]
    )
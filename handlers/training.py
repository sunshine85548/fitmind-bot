from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import aiosqlite

from keyboards.inline import (
    get_level_keyboard,
    get_workout_type_keyboard,
    get_done_keyboard
)

from services.workouts import WORKOUTS
from core.database import DB_NAME

router = Router()


@router.message(Command("training"))
async def training(message: Message):

    await message.answer(
        "🏋️ Обери свій рівень підготовки:",
        reply_markup=get_level_keyboard()
    )


@router.callback_query(lambda c: c.data.startswith("level_"))
async def choose_workout_type(callback: CallbackQuery):

    level = callback.data.split("_")[1]

    await callback.message.edit_text(
        "💪 Обери тип тренування:",
        reply_markup=get_workout_type_keyboard(level)
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("workout_"))
async def send_workout(callback: CallbackQuery):

    _, level, workout_type = callback.data.split("_")

    workout_key = f"{level}_{workout_type}"

    workout = WORKOUTS.get(workout_key)

    if not workout:
        await callback.message.answer(
            "❌ Тренування не знайдено."
        )
        return

    text = (
        f"{workout['title']}\n\n"
        f"{workout['text']}"
    )

    await callback.message.answer(
        text,
        reply_markup=get_done_keyboard(workout_key)
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("done_"))
async def done_workout(callback: CallbackQuery):

    workout_key = callback.data.replace("done_", "")

    parts = workout_key.split("_")

    difficulty = parts[0]
    workout_type = parts[1]

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO workout_logs
            (user_id, workout_type, difficulty)
            VALUES (?, ?, ?)
            """,
            (
                callback.from_user.id,
                workout_type,
                difficulty
            )
        )

        await db.commit()

    await callback.message.answer(
        "✅ Тренування успішно збережено!"
    )

    await callback.answer()
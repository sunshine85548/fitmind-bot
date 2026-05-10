from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.inline import get_done_keyboard
import aiosqlite

from keyboards.inline import (
    get_level_keyboard,
    get_workout_type_keyboard
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
        await callback.message.answer("❌ Тренування не знайдено.")
        return

    text = (
        f"{workout['title']}\n\n"
        f"{workout['text']}"
    )

    await callback.message.answer(
    text,
    reply_markup=get_done_keyboard(1)
)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO activity_logs (user_id, exercise_id) VALUES (?, ?)",
            (callback.from_user.id, 1)
        )
        await db.commit()

    await callback.answer()
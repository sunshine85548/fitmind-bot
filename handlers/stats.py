from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite

from core.database import DB_NAME

router = Router()


@router.message(Command("stats"))
async def show_stats(message: Message):

    async with aiosqlite.connect(DB_NAME) as db:

        async with db.execute(
            """
            SELECT COUNT(*)
            FROM workout_logs
            WHERE user_id = ?
            AND datetime(timestamp) >= datetime('now', '-7 day')
            """,
            (message.from_user.id,)
        ) as cursor:

            week_count = await cursor.fetchone()

        async with db.execute(
            """
            SELECT COUNT(DISTINCT date(timestamp))
            FROM workout_logs
            WHERE user_id = ?
            AND datetime(timestamp) >= datetime('now', '-30 day')
            """,
            (message.from_user.id,)
        ) as cursor:

            active_days = await cursor.fetchone()

        async with db.execute(
            """
            SELECT COUNT(*)
            FROM workout_logs
            WHERE user_id = ?
            """,
            (message.from_user.id,)
        ) as cursor:

            total_workouts = await cursor.fetchone()

    week_trainings = week_count[0]
    active_days_count = active_days[0]
    total = total_workouts[0]

    if week_trainings >= 10:
        level = "🔥 Machine"

    elif week_trainings >= 5:
        level = "💪 Active"

    elif week_trainings >= 1:
        level = "🟢 Beginner"

    else:
        level = "⚪ Новачок"

    text = (
        f"📊 <b>FitMind Statistics</b>\n\n"

        f"🏋️ Тренувань за 7 днів: <b>{week_trainings}</b>\n"
        f"📅 Активних днів за 30 днів: <b>{active_days_count}</b>\n"
        f"🔥 Всього тренувань: <b>{total}</b>\n\n"

        f"⚡ Рівень активності: <b>{level}</b>"
    )

    await message.answer(text)

@router.message(Command("history"))
async def workout_history(message: Message):

    async with aiosqlite.connect(DB_NAME) as db:

        async with db.execute(
            """
            SELECT workout_type, difficulty, timestamp
            FROM workout_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            (message.from_user.id,)
        ) as cursor:

            workouts = await cursor.fetchall()

    if not workouts:

        await message.answer(
            "📭 Історія тренувань порожня."
        )

        return

    text = "📅 <b>Історія тренувань</b>\n\n"

    for workout_type, difficulty, timestamp in workouts:

        workout_emoji = {
            "push": "💪",
            "pull": "🏋️",
            "legs": "🦵",
            "fullbody": "🔥"
        }.get(workout_type, "🏋️")

        difficulty_text = {
            "beginner": "Новачок",
            "advanced": "Досвідчений"
        }.get(difficulty, difficulty)

        text += (
            f"{workout_emoji} "
            f"<b>{workout_type.title()}</b> | "
            f"{difficulty_text}\n"
            f"🕒 {timestamp[:16]} UTC\n\n"
        )

    await message.answer(text)
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
            FROM activity_logs
            WHERE user_id = ?
            AND datetime(timestamp) >= datetime('now', '-7 day')
            """,
            (message.from_user.id,)
        ) as cursor:

            week_count = await cursor.fetchone()

        async with db.execute(
            """
            SELECT COUNT(DISTINCT date(timestamp))
            FROM activity_logs
            WHERE user_id = ?
            AND datetime(timestamp) >= datetime('now', '-30 day')
            """,
            (message.from_user.id,)
        ) as cursor:

            active_days = await cursor.fetchone()

        async with db.execute(
            """
            SELECT COUNT(*)
            FROM activity_logs
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
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
            streak = await cursor.fetchone()

    text = (
        f"📊 <b>Твоя статистика</b>\n\n"
        f"Тренувань за 7 днів: <b>{week_count[0]}</b>\n"
        f"Активних днів за 30 днів: <b>{streak[0]}</b>"
    )

    await message.answer(text)
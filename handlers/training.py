from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite
import random
from core.database import DB_NAME

router = Router()


@router.message(Command("training"))
async def training(message: Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT ex_id, title, description FROM exercises ORDER BY RANDOM() LIMIT 1"
        ) as cursor:
            exercise = await cursor.fetchone()

    if not exercise:
        await message.answer("База вправ поки порожня.")
        return

    ex_id, title, description = exercise

    text = (
        f"🏋️ <b>Тренування</b>\n\n"
        f"Вправа: <b>{title}</b>\n"
        f"{description}\n\n"
        f"Після виконання напиши: /done {ex_id}"
    )

    await message.answer(text)


@router.message(Command("done"))
async def done_training(message: Message):
    try:
        ex_id = int(message.text.split()[1])
    except:
        await message.answer("Формат: /done ID")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO activity_logs (user_id, exercise_id) VALUES (?, ?)",
            (message.from_user.id, ex_id)
        )
        await db.commit()

    await message.answer("✅ Тренування зафіксовано!")
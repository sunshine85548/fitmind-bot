from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import aiosqlite
from keyboards.inline import get_done_keyboard
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
        f"{description}"
    )

    await message.answer(
        text,
        reply_markup=get_done_keyboard(ex_id)
    )


@router.callback_query(lambda c: c.data.startswith("done_"))
async def done_training(callback: CallbackQuery):
    ex_id = int(callback.data.split("_")[1])

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO activity_logs (user_id, exercise_id) VALUES (?, ?)",
            (callback.from_user.id, ex_id)
        )
        await db.commit()

    await callback.message.answer("✅ Тренування зафіксовано!")
    await callback.answer()
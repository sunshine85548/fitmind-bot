from aiogram import Router
from aiogram.types import Message
from keyboards.reply import get_main_keyboard
from aiogram.filters import CommandStart, Command
from handlers.user_profile import show_profile, show_goals
from handlers.stats import show_stats, workout_history
from handlers.training import training
from aiogram.fsm.context import FSMContext
import aiosqlite

from core.database import DB_NAME

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):

    await state.clear()

    async with aiosqlite.connect(DB_NAME) as db:

        async with db.execute(
            "SELECT username FROM users WHERE user_id = ?",
            (message.from_user.id,)
        ) as cursor:

            user = await cursor.fetchone()

    if user:

        welcome_text = (
            f"З поверненням, "
            f"<b>{message.from_user.first_name}</b>!\n\n"

            f"👤 Переглянути профіль: /profile\n"
            f"🎯 Твої цілі: /goals\n"
            f"❓ Довідка: /help"
        )

    else:

        welcome_text = (
            f"Привіт, "
            f"<b>{message.from_user.first_name}</b>! 👋\n\n"

            f"Я — <b>FitMind Bot</b>, "
            f"твій персональний фітнес-асистент.\n\n"

            f"⚙️ Заповни профіль: /update\n"
            f"❓ Довідка: /help"
        )

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):

    help_text = (
        f"🤖 <b>FitMind Bot — Команди</b>\n\n"

        f"👤 <b>Профіль</b>\n"
        f"/profile — перегляд профілю\n"
        f"/update — оновлення анкети\n\n"

        f"🎯 <b>Цілі</b>\n"
        f"/goals — список цілей\n"
        f"/add_goal — створити ціль\n"
        f"/update_goal — оновити прогрес\n"
        f"/delete_goal — видалити ціль\n\n"

        f"🏋️ <b>Тренування</b>\n"
        f"/training — отримати тренування\n"
        f"/history — історія тренувань\n\n"

        f"📊 <b>Статистика</b>\n"
        f"/stats — статистика активності\n\n"

        f"❌ <b>FSM</b>\n"
        f"/cancel — скасувати поточну дію"
    )

    await message.answer(help_text)


@router.message(lambda message: message.text == "👤 Профіль")
async def profile_button(message: Message):

    await show_profile(message)


@router.message(lambda message: message.text == "🎯 Цілі")
async def goals_button(message: Message):

    await show_goals(message)


@router.message(lambda message: message.text == "📊 Статистика")
async def stats_button(message: Message):

    await show_stats(message)


@router.message(lambda message: message.text == "🏋️ Тренування")
async def training_button(message: Message):

    await training(message)


@router.message(lambda message: message.text == "📅 Історія")
async def history_button(message: Message):

    await workout_history(message)


@router.message(lambda message: message.text == "❓ Допомога")
async def help_button(message: Message):

    await cmd_help(message)
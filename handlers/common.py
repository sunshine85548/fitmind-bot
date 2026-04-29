from aiogram import Router
from aiogram.types import Message
from keyboards.reply import get_main_keyboard
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import aiosqlite
from core.database import DB_NAME

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username FROM users WHERE user_id = ?", (message.from_user.id,)) as cursor:
            user = await cursor.fetchone()

    if user:
        welcome_text = (
            f"З поверненням, <b>{message.from_user.first_name}</b>!\n"
            f"Твій профіль вже налаштований.\n\n"
            f" Переглянути профіль: /profile\n"
            f" Твої цілі: /goals\n"
            f" Довідка: /help"
        )
    else:
        welcome_text = (
            f"Привіт, <b>{message.from_user.first_name}</b>! 👋\n\n"
            f"Я — <b>FitMind Bot</b>, твій персональний фітнес-асистент.\n"
            f"Я допоможу тобі розрахувати норму калорій, відстежувати цілі та тренування.\n\n"
            f" Щоб почати роботу, заповни свій профіль: /update\n"
            f" Довідка по командах: /help"
        )

    await message.answer(welcome_text, reply_markup=get_main_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "<b>Довідка по командах:</b>\n\n"
        " <b>Профіль:</b>\n"
        "/profile — Переглянути свій профіль\n"
        "/update — Оновити або заповнити дані\n\n"
        " <b>Цілі:</b>\n"
        "/goals — Список твоїх цілей\n"
        "/add_goal — Додати нову ціль\n"
        "/complete_goal [ID] — Відмітити ціль як виконану\n"
        "/delete_goal [ID] — Видалити ціль\n\n"
        "/cancel — Скасувати поточну дію"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())

@router.message(lambda message: message.text == "👤 Профіль")
async def profile_button(message: Message):
    await message.answer("Скористайся командою /profile", reply_markup=get_main_keyboard())


@router.message(lambda message: message.text == "🎯 Цілі")
async def goals_button(message: Message):
    await message.answer("Скористайся командою /goals", reply_markup=get_main_keyboard())


@router.message(lambda message: message.text == "📊 Статистика")
async def stats_button(message: Message):
    await message.answer("Розділ статистики скоро буде доступний.", reply_markup=get_main_keyboard())


@router.message(lambda message: message.text == "🏋️ Тренування")
async def training_button(message: Message):
    await message.answer("Розділ тренувань скоро буде доступний.", reply_markup=get_main_keyboard())


@router.message(lambda message: message.text == "❓ Допомога")
async def help_button(message: Message):
    await cmd_help(message)
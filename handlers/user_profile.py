from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

from services.math_calc import calculate_bmi, calculate_bmr
from core.database import DB_NAME
from keyboards.inline import get_update_keyboard

router = Router()


class ProfileStates(StatesGroup):
    gender = State()
    weight = State()
    height = State()
    age = State()
    goal = State()


class EditSpecificState(StatesGroup):
    waiting_for_new_weight = State()
    waiting_for_new_height = State()
    waiting_for_new_age = State()


class AddGoalStates(StatesGroup):

    title = State()

    target_value = State()

    unit = State()

@router.message(Command("cancel"), StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Вам немає чого скасовувати. Використовуйте /help для списку команд."
        )
        return

    await state.clear()
    await message.answer("❌ Дію скасовано. Повернуто до головного меню.")


@router.message(Command("profile"))
async def show_profile(message: Message):

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT weight, height, age, gender, goal, bmr FROM users WHERE user_id = ?",
            (message.from_user.id,)
        ) as cursor:
            user = await cursor.fetchone()

    if user:
        weight, height, age, gender, goal, bmr = user

        bmi = round(calculate_bmi(weight, height), 2)
        bmr = round(bmr, 2)

        text = (
            f"🔥 <b>FitMind Profile</b>\n\n"

            f"👤 Стать: <b>{gender}</b>\n"
            f"🎂 Вік: <b>{age}</b>\n"
            f"📏 Зріст: <b>{height} см</b>\n"
            f"⚖️ Вага: <b>{weight} кг</b>\n\n"

            f"🎯 Ціль: <b>{goal}</b>\n"
            f"📊 ІМТ: <b>{bmi}</b>\n"
            f"🔥 Добова норма калорій: <b>{bmr} ккал</b>\n\n"

            f"⚙️ Оновити дані: /update"
        )

        await message.answer(text)

    else:
        await message.answer(
            "Профіль не знайдено. Введіть /update, щоб заповнити анкету."
        )


@router.message(Command("update"))
async def start_fsm(message: Message, state: FSMContext):

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (message.from_user.id,)
        ) as cursor:
            user = await cursor.fetchone()

    if user:
        await message.answer(
            "Що саме ви хочете оновити?",
            reply_markup=get_update_keyboard()
        )
    else:
        await state.set_state(ProfileStates.gender)
        await message.answer("Вкажіть вашу стать (Чоловік/Жінка):")


@router.callback_query(F.data == "edit_all")
async def edit_all_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Починаємо з початку. Вкажіть вашу стать (Чоловік/Жінка):"
    )

    await state.set_state(ProfileStates.gender)


@router.callback_query(F.data == "edit_weight")
async def edit_weight_callback(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "Введіть вашу нову вагу (у кг):"
    )

    await state.set_state(EditSpecificState.waiting_for_new_weight)


@router.message(
    EditSpecificState.waiting_for_new_weight,
    F.text.regexp(r'^\d+(\.\d+)?$')
)
async def process_new_weight(message: Message, state: FSMContext):

    new_weight = float(message.text)

    if not (30 <= new_weight <= 300):
        await message.answer(
            "❌ Введіть реальну вагу (від 30 до 300 кг)."
        )
        return

    await update_single_field_and_recalculate(
        message.from_user.id,
        "weight",
        new_weight
    )

    await state.clear()

    await message.answer(
        "✅ Вагу успішно оновлено! BMR перераховано."
    )


@router.message(EditSpecificState.waiting_for_new_weight)
async def process_new_weight_invalid(message: Message):

    await message.answer(
        "Помилка! Введіть коректне число для ваги."
    )


@router.callback_query(F.data == "edit_height")
async def edit_height_callback(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "Введіть ваш новий зріст (у см):"
    )

    await state.set_state(EditSpecificState.waiting_for_new_height)


@router.message(
    EditSpecificState.waiting_for_new_height,
    F.text.regexp(r'^\d+(\.\d+)?$')
)
async def process_new_height(message: Message, state: FSMContext):

    new_height = float(message.text)

    if not (100 <= new_height <= 250):
        await message.answer(
            "❌ Введіть реальний зріст."
        )
        return

    await update_single_field_and_recalculate(
        message.from_user.id,
        "height",
        new_height
    )

    await state.clear()

    await message.answer(
        "✅ Зріст успішно оновлено!"
    )


@router.callback_query(F.data == "edit_age")
async def edit_age_callback(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "Введіть ваш новий вік:"
    )

    await state.set_state(EditSpecificState.waiting_for_new_age)


@router.message(
    EditSpecificState.waiting_for_new_age,
    F.text.regexp(r'^\d+$')
)
async def process_new_age(message: Message, state: FSMContext):

    new_age = int(message.text)

    if not (10 <= new_age <= 120):
        await message.answer(
            "❌ Введіть реальний вік."
        )
        return

    await update_single_field_and_recalculate(
        message.from_user.id,
        "age",
        new_age
    )

    await state.clear()

    await message.answer(
        "✅ Вік успішно оновлено!"
    )


async def update_single_field_and_recalculate(
    user_id: int,
    field_name: str,
    new_value
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            f"UPDATE users SET {field_name} = ? WHERE user_id = ?",
            (new_value, user_id)
        )

        async with db.execute(
            "SELECT weight, height, age, gender FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:

            user_data = await cursor.fetchone()

        weight, height, age, gender = user_data

        new_bmr = calculate_bmr(
            weight,
            height,
            age,
            gender
        )

        await db.execute(
            "UPDATE users SET bmr = ? WHERE user_id = ?",
            (new_bmr, user_id)
        )

        await db.commit()

@router.message(Command("add_goal"))
async def start_add_goal(message: Message, state: FSMContext):

    await state.set_state(AddGoalStates.title)

    await message.answer(
        "🎯 Введіть назву цілі:"
    )


@router.message(AddGoalStates.title)
async def process_goal_title(message: Message, state: FSMContext):

    await state.update_data(
        title=message.text
    )

    await state.set_state(AddGoalStates.target_value)

    await message.answer(
        "📈 Введіть цільове значення:"
    )


@router.message(
    AddGoalStates.target_value,
    F.text.regexp(r'^\d+(\.\d+)?$')
)
async def process_goal_target(message: Message, state: FSMContext):

    await state.update_data(
        target_value=float(message.text)
    )

    await state.set_state(AddGoalStates.unit)

    await message.answer(
        "📏 Введіть одиницю вимірювання (кг, км, днів):"
    )


@router.message(AddGoalStates.unit)
async def process_goal_unit(message: Message, state: FSMContext):

    data = await state.get_data()

    title = data["title"]
    target_value = data["target_value"]
    unit = message.text

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO user_goals
            (user_id, title, target_value, unit)
            VALUES (?, ?, ?, ?)
            """,
            (
                message.from_user.id,
                title,
                target_value,
                unit
            )
        )

        await db.commit()

    await state.clear()

    await message.answer(
        "✅ Ціль успішно створено!"
    )

@router.message(
    ProfileStates.gender,
    F.text.in_(["Чоловік", "Жінка"])
)
async def process_gender(message: Message, state: FSMContext):

    await state.update_data(
        gender=message.text
    )

    await state.set_state(ProfileStates.weight)

    await message.answer(
        "⚖️ Введіть вашу вагу (кг):"
    )


@router.message(
    ProfileStates.weight,
    F.text.regexp(r'^\d+(\.\d+)?$')
)
async def process_weight(message: Message, state: FSMContext):

    weight = float(message.text)

    if not (30 <= weight <= 300):

        await message.answer(
            "❌ Введіть реальну вагу."
        )

        return

    await state.update_data(
        weight=weight
    )

    await state.set_state(ProfileStates.height)

    await message.answer(
        "📏 Введіть ваш зріст (см):"
    )


@router.message(
    ProfileStates.height,
    F.text.regexp(r'^\d+(\.\d+)?$')
)
async def process_height(message: Message, state: FSMContext):

    height = float(message.text)

    if not (100 <= height <= 250):

        await message.answer(
            "❌ Введіть реальний зріст."
        )

        return

    await state.update_data(
        height=height
    )

    await state.set_state(ProfileStates.age)

    await message.answer(
        "🎂 Введіть ваш вік:"
    )


@router.message(
    ProfileStates.age,
    F.text.regexp(r'^\d+$')
)
async def process_age(message: Message, state: FSMContext):

    age = int(message.text)

    if not (10 <= age <= 120):

        await message.answer(
            "❌ Введіть реальний вік."
        )

        return

    await state.update_data(
        age=age
    )

    await state.set_state(ProfileStates.goal)

    await message.answer(
        "🎯 Ваша ціль?\n"
        "(Схуднення / Маса / Підтримка)"
    )


@router.message(ProfileStates.goal)
async def process_goal(message: Message, state: FSMContext):

    data = await state.get_data()

    gender = data["gender"]
    weight = data["weight"]
    height = data["height"]
    age = data["age"]

    goal = message.text

    bmr = calculate_bmr(
        weight,
        height,
        age,
        gender
    )

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR REPLACE INTO users
            (user_id, username, weight, height,
             age, gender, goal, bmr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message.from_user.id,
                message.from_user.username,
                weight,
                height,
                age,
                gender,
                goal,
                bmr
            )
        )

        await db.commit()

    await state.clear()

    bmi = round(
        calculate_bmi(weight, height),
        2
    )

    await message.answer(
        f"✅ Профіль успішно створено!\n\n"
        f"📊 BMI: {bmi}\n"
        f"🔥 BMR: {round(bmr, 2)} ккал"
    )


@router.message(Command("goals"))
async def show_goals(message: Message):

    async with aiosqlite.connect(DB_NAME) as db:

        async with db.execute(
            """
            SELECT
                goal_id,
                title,
                current_value,
                target_value,
                unit,
                is_completed
            FROM user_goals
            WHERE user_id = ?
            """,
            (message.from_user.id,)
        ) as cursor:

            goals = await cursor.fetchall()

    if not goals:

        await message.answer(
            "🎯 У вас поки немає цілей.\n\n"
            "Створіть через /add_goal"
        )

        return

    text = "🎯 <b>Ваші цілі</b>\n\n"

    for goal in goals:

        (
            goal_id,
            title,
            current_value,
            target_value,
            unit,
            is_completed
        ) = goal

        progress = min(
            round((current_value / target_value) * 100),
            100
        )

        status = "✅" if is_completed else "📈"

        text += (
            f"{status} <b>{title}</b>\n"

            f"{current_value} / "
            f"{target_value} {unit}\n"

            f"Прогрес: {progress}%\n"

            f"ID: {goal_id}\n\n"
        )

    await message.answer(text)

@router.message(Command("update_goal"))
async def update_goal_progress(message: Message):

    parts = message.text.split()

    if len(parts) != 3:

        await message.answer(
            "Формат:\n/update_goal ID значення"
        )

        return

    try:

        goal_id = int(parts[1])

        new_value = float(parts[2])

    except:

        await message.answer(
            "❌ Некоректні дані."
        )

        return

    async with aiosqlite.connect(DB_NAME) as db:

        async with db.execute(
            """
            SELECT target_value
            FROM user_goals
            WHERE goal_id = ?
            AND user_id = ?
            """,
            (
                goal_id,
                message.from_user.id
            )
        ) as cursor:

            goal = await cursor.fetchone()

        if not goal:

            await message.answer(
                "❌ Ціль не знайдено."
            )

            return

        target_value = goal[0]

        is_completed = int(new_value >= target_value)

        await db.execute(
            """
            UPDATE user_goals
            SET current_value = ?,
                is_completed = ?
            WHERE goal_id = ?
            """,
            (
                new_value,
                is_completed,
                goal_id
            )
        )

        await db.commit()

    await message.answer(
        "✅ Прогрес цілі оновлено!"
    )

@router.message(Command("delete_goal"))
async def delete_goal(message: Message):

    parts = message.text.split()

    if len(parts) != 2:

        await message.answer(
            "Формат:\n/delete_goal ID"
        )

        return

    try:

        goal_id = int(parts[1])

    except:

        await message.answer(
            "❌ Некоректний ID."
        )

        return

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM user_goals
            WHERE goal_id = ?
            AND user_id = ?
            """,
            (
                goal_id,
                message.from_user.id
            )
        )

        await db.commit()

    await message.answer(
        "🗑 Ціль видалено!"
    )
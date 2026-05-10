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

@router.message(Command("cancel"), StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Вам немає чого скасовувати. Використовуйте /help для списку команд.")
        return
    await state.clear()
    await message.answer(" Дію скасовано. Повернуто до головного меню.")


@router.message(Command("profile"))
async def show_profile(message: Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT weight, height, age, gender, goal, bmr FROM users WHERE user_id = ?",
                              (message.from_user.id,)) as cursor:
            user = await cursor.fetchone()

    if user:
        weight, height, age, gender, goal, bmr = user
        bmi = calculate_bmi(weight, height)
        text = (f" <b>Твій Профіль:</b>\n"
                f"Стать: <b>{gender}</b>\n"
                f"Вік: <b>{age}</b>\n"
                f"Зріст: <b>{height} см</b>\n"
                f"Вага: <b>{weight} кг</b>\n\n"
                f" Ціль: <b>{goal}</b>\n"
                f" ІМТ: <b>{bmi}</b>\n"
                f" Норма калорій: <b>{bmr} ккал</b>\n\n"
                f" Оновити дані: /update")
        await message.answer(text)
    else:
        await message.answer("Профіль не знайдено. Введіть /update, щоб заповнити анкету.")





@router.message(Command("update"))
async def start_fsm(message: Message, state: FSMContext):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (message.from_user.id,)) as cursor:
            user = await cursor.fetchone()

    if user:
        await message.answer("Що саме ви хочете оновити?", reply_markup=get_update_keyboard())
    else:
        await state.set_state(ProfileStates.gender)
        await message.answer("Вкажіть вашу стать (Чоловік/Жінка):")


#ОБРОБНИКИ КНОПОК ТОЧКОВОГО ОНОВЛЕННЯ

@router.callback_query(F.data == "edit_all")
async def edit_all_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Починаємо з початку. Вкажіть вашу стать (Чоловік/Жінка):")
    await state.set_state(ProfileStates.gender)


#ОБРОБНИКИ КНОПОК ТОЧКОВОГО ОНОВЛЕННЯ

@router.callback_query(F.data == "edit_all")
async def edit_all_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Починаємо з початку. Вкажіть вашу стать (Чоловік/Жінка):")
    await state.set_state(ProfileStates.gender)


#ВАГА
@router.callback_query(F.data == "edit_weight")
async def edit_weight_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введіть вашу нову вагу (у кг):")
    await state.set_state(EditSpecificState.waiting_for_new_weight)


@router.message(EditSpecificState.waiting_for_new_weight, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_new_weight(message: Message, state: FSMContext):
    new_weight = float(message.text)
    if not (30 <= new_weight <= 300):
        await message.answer(" Введіть реальну вагу (від 30 до 300 кг).")
        return

    await update_single_field_and_recalculate(message.from_user.id, "weight", new_weight)
    await state.clear()
    await message.answer(" Вагу успішно оновлено! BMR перераховано. Перевірте: /profile")


@router.message(EditSpecificState.waiting_for_new_weight)
async def process_new_weight_invalid(message: Message):
    await message.answer("Помилка! Введіть коректне число для ваги (наприклад, 75 або 75.5).")


#ЗРІСТ
@router.callback_query(F.data == "edit_height")
async def edit_height_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введіть ваш новий зріст (у см):")
    await state.set_state(EditSpecificState.waiting_for_new_height)


@router.message(EditSpecificState.waiting_for_new_height, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_new_height(message: Message, state: FSMContext):
    new_height = float(message.text)
    if not (100 <= new_height <= 250):
        await message.answer(" Введіть реальний зріст (від 100 до 250 см).")
        return

    await update_single_field_and_recalculate(message.from_user.id, "height", new_height)
    await state.clear()
    await message.answer(" Зріст успішно оновлено! BMR перераховано. Перевірте: /profile")


@router.message(EditSpecificState.waiting_for_new_height)
async def process_new_height_invalid(message: Message):
    await message.answer("Помилка! Введіть коректне число для зросту.")


#ВІК
@router.callback_query(F.data == "edit_age")
async def edit_age_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введіть ваш новий вік (лише ціле число):")
    await state.set_state(EditSpecificState.waiting_for_new_age)


@router.message(EditSpecificState.waiting_for_new_age, F.text.regexp(r'^\d+$'))
async def process_new_age(message: Message, state: FSMContext):
    new_age = int(message.text)
    if not (10 <= new_age <= 120):
        await message.answer(" Введіть реальний вік (від 10 до 120 років).")
        return

    await update_single_field_and_recalculate(message.from_user.id, "age", new_age)
    await state.clear()
    await message.answer(" Вік успішно оновлено! BMR перераховано. Перевірте: /profile")


@router.message(EditSpecificState.waiting_for_new_age)
async def process_new_age_invalid(message: Message):
    await message.answer("Помилка! Введіть коректне ціле число для віку.")


#ФУНКЦІЯ ПЕРЕРАХУНКУ
async def update_single_field_and_recalculate(user_id: int, field_name: str, new_value):

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE users SET {field_name} = ? WHERE user_id = ?", (new_value, user_id))

        async with db.execute("SELECT weight, height, age, gender FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user_data = await cursor.fetchone()

        weight, height, age, gender = user_data
        new_bmr = calculate_bmr(weight, height, age, gender)

        await db.execute("UPDATE users SET bmr = ? WHERE user_id = ?", (new_bmr, user_id))
        await db.commit()
#ЗАХИСТ СТАТІ
@router.message(ProfileStates.gender, F.text.lower().in_(["чоловік", "жінка", "чоловіча", "жіноча"]))
async def process_gender(message: Message, state: FSMContext):
    user_text = message.text.lower()
    standardized_gender = "Чоловік" if user_text in ["чоловік", "чоловіча"] else "Жінка"

    await state.update_data(gender=standardized_gender)
    await state.set_state(ProfileStates.weight)
    await message.answer("Введіть вашу вагу (у кг, лише число):")


@router.message(ProfileStates.gender)
async def process_gender_invalid(message: Message):
    if not message.text:
        await message.answer("Будь ласка, надішліть текст, а не медіафайл чи стікер.")
        return
    await message.answer("Помилка! Введіть стать коректно: Чоловік або Жінка (можна також 'чоловіча' чи 'жіноча').")


#ЗАХИСТ ВАГИ
@router.message(ProfileStates.weight, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_weight(message: Message, state: FSMContext):
    weight = float(message.text)
    if not (30 <= weight <= 300):
        await message.answer("Будь ласка, введіть реальну вагу (від 30 до 300 кг).")
        return

    await state.update_data(weight=weight)
    await state.set_state(ProfileStates.height)
    await message.answer("Введіть ваш зріст (у см, лише число):")


@router.message(ProfileStates.weight)
async def process_weight_invalid(message: Message):
    if not message.text:
        await message.answer("Будь ласка, надішліть число текстом, а не медіафайл чи стікер.")
        return
    await message.answer("Помилка! Введіть коректне число для ваги (наприклад, 75 або 75.5).")


#ЗАХИСТ ЗРОСТУ
@router.message(ProfileStates.height, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_height(message: Message, state: FSMContext):
    height = float(message.text)
    if not (100 <= height <= 250):
        await message.answer("Будь ласка, введіть реальний зріст (від 100 до 250 см).")
        return

    await state.update_data(height=height)
    await state.set_state(ProfileStates.age)
    await message.answer("Введіть ваш вік (лише ціле число):")


@router.message(ProfileStates.height)
async def process_height_invalid(message: Message):
    if not message.text:
        await message.answer("Будь ласка, надішліть число текстом, а не медіафайл чи стікер.")
        return
    await message.answer("Помилка! Введіть коректне число для зросту.")


#ЗАХИСТ ВІКУ
@router.message(ProfileStates.age, F.text.regexp(r'^\d+$'))
async def process_age(message: Message, state: FSMContext):
    age = int(message.text)
    if not (10 <= age <= 120):
        await message.answer("Будь ласка, введіть реальний вік (від 10 до 120 років).")
        return

    await state.update_data(age=age)
    await state.set_state(ProfileStates.goal)
    await message.answer("Яка ваша ціль (Схуднення / Підтримка / Набір маси)?")


@router.message(ProfileStates.age)
async def process_age_invalid(message: Message):
    if not message.text:
        await message.answer("Будь ласка, надішліть число текстом, а не медіафайл чи стікер.")
        return
    await message.answer("Помилка! Введіть коректне ціле число для віку.")


#ЗАХИСТ ЦІЛІ
@router.message(ProfileStates.goal, F.text.lower().in_(["схуднення", "підтримка", "набір маси"]))
async def process_goal(message: Message, state: FSMContext):
    data = await state.get_data()
    weight = data['weight']
    height = data['height']
    age = data['age']
    gender = data['gender']
    goal = message.text.capitalize()

    bmr = calculate_bmr(weight, height, age, gender)

    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('''
                INSERT INTO users (user_id, username, weight, height, age, gender, goal, bmr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username, weight=excluded.weight, height=excluded.height,
                age=excluded.age, gender=excluded.gender, goal=excluded.goal, bmr=excluded.bmr
            ''', (message.from_user.id, message.from_user.username, weight, height, age, gender, goal, bmr))
            await db.commit()
    except Exception as e:
        await message.answer("Сталася помилка при збереженні бази даних. Спробуйте пізніше.")
        print(f"DB Error: {e}")
        return

    await state.clear()
    await message.answer("Анкету успішно збережено! Переглянути: /profile")


@router.message(ProfileStates.goal)
async def process_goal_invalid(message: Message):
    if not message.text:
        await message.answer("Будь ласка, надішліть текст, а не медіафайл чи стікер.")
        return
    await message.answer("Помилка! Введіть одну з цілей: Схуднення, Підтримка або Набір маси.")


#СИСТЕМА ЦІЛЕЙ КОРИСТУВАЧА

class AddGoalStates(StatesGroup):
    title = State()


@router.message(Command("add_goal"))
async def start_add_goal(message: Message, state: FSMContext):
    await state.set_state(AddGoalStates.title)
    await message.answer("Напишіть вашу нову фітнес-ціль (наприклад: 'Пробігти 5 км', 'Схуднути на 2 кг'):")


@router.message(AddGoalStates.title)
async def process_add_goal(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Будь ласка, надішліть текст, а не медіафайл чи стікер.")
        return

    goal_title = message.text

    if not (3 <= len(goal_title) <= 100):
        await message.answer(" Ціль має містити від 3 до 100 символів. Спробуйте ще раз або напишіть /cancel:")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO user_goals (user_id, title) VALUES (?, ?)",
            (message.from_user.id, goal_title)
        )
        await db.commit()

    await state.clear()
    await message.answer("Ціль успішно додано! Переглянути ваші цілі: /goals")


@router.message(Command("goals"))
async def show_goals(message: Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT goal_id, title, is_completed FROM user_goals WHERE user_id = ?",
                (message.from_user.id,)
        ) as cursor:
            goals = await cursor.fetchall()

    if not goals:
        await message.answer("У вас поки немає цілей. Додайте першу: /add_goal")
        return

    text = " Ваші цілі:\n\n"
    for goal in goals:
        goal_id, title, is_completed = goal
        status = "✅" if is_completed else "⏳"
        text += f"{status} {title} (ID: {goal_id})\n"

    text += "\nЩоб додати нову: /add_goal\nЩоб відмітити як виконану: напишіть /complete_goal і через пробіл ID цілі"
    await message.answer(text)


@router.message(Command("complete_goal"))
async def complete_goal(message: Message):
    try:
        goal_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Помилка! Використовуйте формат: /complete_goal [ID_цілі]")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT is_completed FROM user_goals WHERE goal_id = ? AND user_id = ?",
                              (goal_id, message.from_user.id)) as cursor:
            goal = await cursor.fetchone()

        if not goal:
            await message.answer("Ціль з таким ID не знайдено.")
            return

        if goal[0]:
            await message.answer("Цю ціль вже було виконано раніше!")
            return

        await db.execute(
            "UPDATE user_goals SET is_completed = 1 WHERE goal_id = ? AND user_id = ?",
            (goal_id, message.from_user.id)
        )
        await db.commit()

    await message.answer(f"Вітаю! Ціль №{goal_id} успішно виконана!")


@router.message(Command("delete_goal"))
async def delete_goal(message: Message):
    try:
        goal_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Помилка! Використовуйте формат: /delete_goal [ID_цілі]")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT goal_id FROM user_goals WHERE goal_id = ? AND user_id = ?",
                              (goal_id, message.from_user.id)) as cursor:
            goal = await cursor.fetchone()

        if not goal:
            await message.answer("Ціль з таким ID не знайдено.")
            return

        await db.execute("DELETE FROM user_goals WHERE goal_id = ? AND user_id = ?", (goal_id, message.from_user.id))
        await db.commit()

    await message.answer(f"🗑 Ціль №{goal_id} успішно видалено!")
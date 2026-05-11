# FitMind Bot

Telegram-бот для фітнес трекінгу, персональної статистики та контролю прогресу користувача.

Проєкт створений на Python з використанням aiogram та SQLite.

---

## Можливості

### Профіль користувача
- Реєстрація через анкету
- Розрахунок BMI та BMR
- Зберігання параметрів користувача
- Оновлення профілю

### Система тренувань
- Готові тренувальні програми
- Вибір рівня підготовки
- Вибір типу тренування
- Push / Pull / Legs / FullBody
- Логування виконаних тренувань
- Історія тренувань

### Система цілей
- Створення персональних цілей
- Відстеження прогресу
- Прогрес у відсотках
- Оновлення прогресу цілей
- Видалення цілей

### Статистика
- Кількість тренувань за 7 днів
- Активні дні за 30 днів
- Загальна кількість тренувань
- Рівень активності користувача

---

## Технології

- Python 3.11+
- aiogram 3.x
- SQLite
- aiosqlite
- python-dotenv
- pytest
- GitHub Actions CI/CD

---

## Архітектура та особливості реалізації

- FSM для анкет та створення цілей
- Асинхронна архітектура aiogram
- Модульна структура проєкту
- Reply Keyboard та Inline Keyboard
- Workout logging system
- Goal progress tracking
- Unit тестування
- Git workflow та CI pipeline

---

## Структура проєкту

```text
fitmind-bot/
│
├── core/               # База даних та конфігурація
├── handlers/           # Telegram handlers
├── keyboards/          # Reply та Inline клавіатури
├── services/           # Бізнес-логіка та тренування
├── tests/              # Unit тести
├── docs/               # UML діаграми
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Команди бота

### Профіль
- `/profile`
- `/update`

### Цілі
- `/goals`
- `/add_goal`
- `/update_goal`
- `/delete_goal`

### Тренування
- `/training`
- `/history`

### Статистика
- `/stats`

### Інше
- `/help`
- `/cancel`

---

## Запуск проєкту

### 1. Клонування репозиторію

```bash
git clone https://github.com/your-username/fitmind-bot.git
cd fitmind-bot
```

### 2. Створення віртуального середовища

```bash
python -m venv venv
```

### 3. Активація середовища

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 5. Створення `.env`

```env
BOT_TOKEN=your_telegram_bot_token
```

### 6. Запуск бота

```bash
python main.py
```

---

## Тестування

Для запуску unit тестів:

```bash
python -m pytest
```

---

## CI (Continuous Integration)

У проєкті використовується GitHub Actions.

При кожному push або pull request автоматично:
- запускаються unit тести
- перевіряється працездатність проєкту

---

## UML Діаграми

### ER Diagram
- `docs/er-diagram.md`

### Use Case Diagram
- `docs/use-case.md`
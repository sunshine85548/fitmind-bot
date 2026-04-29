import aiosqlite
import logging

DB_NAME = "fitmind.db"


async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                weight REAL,
                height REAL,
                age INTEGER,
                gender TEXT,
                goal TEXT,
                bmr REAL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                ex_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                category TEXT,
                description TEXT,
                local_path TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                exercise_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (exercise_id) REFERENCES exercises (ex_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_goals (
                goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        await db.execute("DELETE FROM exercises")

        await db.executemany(
            "INSERT INTO exercises (title, category, description, local_path) VALUES (?, ?, ?, ?)",
            [
                ("Присідання", "Ноги", "3 підходи по 12 повторень", ""),
                ("Віджимання", "Груди", "3 підходи по 15 повторень", ""),
                ("Планка", "Прес", "3 підходи по 30 секунд", ""),
                ("Підтягування", "Спина", "3 підходи максимум", ""),
                ("Жим гантелей", "Плечі", "3 підходи по 12 повторень", "")
            ]
        )

        await db.commit()
        logging.info("База даних та таблиці успішно створені.")
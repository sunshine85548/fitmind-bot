import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from core.config import BOT_TOKEN
from handlers.stats import router as stats_router
from core.database import create_db
from handlers.user_profile import router
from handlers.training import router as training_router as profile_router
from handlers.common import router as common_router

logging.basicConfig(level=logging.INFO)


async def main():
    await create_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(common_router)
    dp.include_router(profile_router)
    dp.include_router(stats_router)
    dp.include_router(training_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущений і готовий до роботи!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бота зупинено вручну.")
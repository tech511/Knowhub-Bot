import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.mongo import close_mongo, connect_mongo
from handlers import setup_routers


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Set it in your environment variables.")

    await connect_mongo()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    setup_routers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_mongo()


if __name__ == "__main__":
    asyncio.run(main())

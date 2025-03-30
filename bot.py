import sys
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from routers.main_router import main_router
# from routers.menu_router import menu_router
# from routers.state_router import state_router
from config import TELEGRAM_BOT_TOKEN
from twitter.tweet_conf import *


async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(bot=bot)
    set_bot(bot)
    dp.include_router(main_router)
    # dp.include_router(menu_router)
    # dp.include_router(state_router)

    commands = [
        types.BotCommand(command="start", description="启动机器人"),
        types.BotCommand(command="kol_tweet_feed", description="获取kOL tweets"),
    ]
    print("now start poling")
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("now bot start running, wait for request")
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())

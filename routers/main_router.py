import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from menus import *
from twitter.tweet_main import *

main_router = Router()

#@main_router.message()
#async def debug_all_messages(message: Message):
#    print(f"收到原始消息: {message.text}")

async def __send_kol_messages__(message: Message, state: FSMContext) -> None:
        user_id = message.from_user.id
        tweets = query_formart_tweet_md(user_id)
        if len(tweets) > 0:
            for tweet in tweets:
                await message.answer(tweet)
                await asyncio.sleep(5)
        else:
           await message.answer("start, no tweet, wait another cycle")


@main_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    __send_kol_messages__(message, state)

@main_router.message(Command("kol_tweet_feed"))
async def command_kol_tweet_feed(message: Message, state: FSMContext) -> None:
    __send_kol_messages__(message, state)

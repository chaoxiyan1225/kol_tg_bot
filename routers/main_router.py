from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.filters import Command
from menus import *
from twitter.tweet_main import *

main_router = Router()
@main_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await message.answer("tweeter start feed back test.")

@main_router.message(Command("kol_tweet_feed"))
async def command_kol_tweet_feed(message: Message, state: FSMContext) -> None:
        # tweets = generate_tweet_list()
        # if len(tweets) > 0:
        #     for tweet in tweets:
        #         await message.answer(tweet)
        await message.answer("tweeter feed back test.")

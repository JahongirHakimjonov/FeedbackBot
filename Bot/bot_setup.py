import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

bot_token = os.getenv('TIIAME_BOT_TOKEN')
if not bot_token:
    raise ValueError("Missing BOT_TOKEN environment variable")


def setup_bot():
    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    return bot, dp

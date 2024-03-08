import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor
from dotenv import load_dotenv, find_dotenv

# Add a new state to the FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Load environment variables
load_dotenv(find_dotenv())

# Now you can access the environment variables as before
API_TOKEN = os.getenv('SUPPORT_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Make sure ADMIN_ID is an integer
GROUP_ID = int(os.getenv('GROUP_ID'))  # Make sure GROUP_ID is an integer

# Logger settings
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher with MemoryStorage
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dbname = os.getenv('SQL_DATABASE')
user = os.getenv('SQL_USER')
password = os.getenv('SQL_PASSWORD')
host = os.getenv('SQL_HOST')


def setup_database():
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, cursor_factory=DictCursor)
        cur = conn.cursor()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn, cur
    except psycopg2.OperationalError as e:
        logging.error(f"Error in database connection: {e}")
        exit(1)


conn, c = setup_database()


# # Create a PostgreSQL table to store user details
# c.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id SERIAL PRIMARY KEY,
#         full_name TEXT,
#         username TEXT,
#         telegram_id INTEGER
#     );
# ''')
# conn.commit()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # Execute the query
    c.execute('SELECT * FROM support_users WHERE telegram_id = %s', (user_id,))

    # Fetch the result
    user_exists = c.fetchall()

    # If user does not exist, insert their details into the database
    if not user_exists:
        c.execute('INSERT INTO support_users (full_name, username, telegram_id) VALUES (%s, %s, %s)',
                  (full_name, username, user_id))
        conn.commit()

    if user_id == ADMIN_ID:
        await message.reply("Salom! Jahongir aka botga xush kelibsiz.")
    else:
        await message.reply(
            "Salom! Talab va takliflaringiz bo‘lsa, ularni yuboring. Barcha gapingizni 1ta xabarda yozing.")


class News(StatesGroup):
    waiting_for_news = State()


# Respond to /news command
@dp.message_handler(commands=['news'])
async def news_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("Assalomu alaykum akajon habarizi yuboring man hammaga jo'nataman:")
        await News.waiting_for_news.set()
    else:
        await message.reply("Adminmassizku nega bosvos uyatmasmi aaa?")


@dp.message_handler(state=News.waiting_for_news, content_types=types.ContentType.ANY)
async def handle_news(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        # Get all users from the database
        c.execute('SELECT telegram_id FROM support_users WHERE telegram_id IS NOT NULL')
        users = c.fetchall()

        for user in users:
            telegram_id = user[0]
            try:
                if telegram_id == ADMIN_ID:
                    continue
                await bot.copy_message(telegram_id, message.chat.id, message.message_id)
            except BotBlocked:
                logging.warning(f"Bot was blocked by the user {telegram_id}")
                continue
            except ChatNotFound:
                logging.warning(f"Chat not found for the user {telegram_id}")
                continue

        await state.finish()
    else:
        await message.reply("Siz admin emassiz dib ettimu!!!")


# Respond to message
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return

    user_id = message.from_user.id
    user_name = message.from_user.full_name
    message_text = message.text

    # Create inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton("Javob berish",
                                              callback_data=str(user_id))  # Store user_id in callback_data
    keyboard.add(reply_button)

    # # Send information to admins with inline keyboard
    # await bot.send_message(
    #     ADMIN_ID,
    #     f"Foydalanuvchi: {user_name}\n"
    #     f"Id: {user_id}\n"
    #     f"Xabar: {message_text}",
    #     reply_markup=keyboard
    # )

    # Send information to group with inline keyboard
    await bot.send_message(
        GROUP_ID,
        f"Foydalanuvchi: {user_name}\n"
        f"Id: {user_id}\n"
        f"Xabar: {message_text}",
        reply_markup=keyboard  # Add inline keyboard to group message
    )


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    user_id = int(callback_query.data)  # Retrieve user_id from callback_data

    # Get the list of administrators in the group
    admins = await bot.get_chat_administrators(GROUP_ID)
    admin_ids = [admin.user.id for admin in admins]

    # Check if the user who pressed the button is an admin
    if callback_query.from_user.id in admin_ids:
        await state.update_data(user_id=user_id)  # Store user_id
        logging.info(f"User_id: {user_id}")
        await bot.send_message(GROUP_ID, "Xabar matnini kiriting:")
        await state.set_state("admin_reply")
    else:
        await bot.send_message(GROUP_ID, "Siz admin emassiz.")
        await state.finish()


@dp.message_handler(state="admin_reply")
async def handle_admin_reply(message: types.Message, state: FSMContext):
    user_data = await state.get_data()  # Get user_id
    user_id = user_data.get("user_id")
    if user_id:
        try:
            await bot.send_message(user_id, message.text)
            await bot.send_message(GROUP_ID, "Habaringiz yuborildi.")  # Send confirmation to admin
            await state.finish()  # Clear user_data
        except Exception as e:
            await bot.send_message(GROUP_ID, f"Xatolik yuz berdi: {e}")  # Send error message to admin
    else:
        await bot.send_message(GROUP_ID, "Xatolik: Foydalanuvchi topilmadi. Iltimos, qaytadan urinib ko'ring.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

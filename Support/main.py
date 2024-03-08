import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import BotBlocked
from dotenv import load_dotenv

# PostgreSQL database connection
from Bot.setup import setup_database

# Add a new state to the FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

load_dotenv()  # take environment variables from .env.

# Now you can access the environment variables as before
API_TOKEN = os.getenv('SUPPORT_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Make sure ADMIN_ID is an integer
GROUP_ID = int(os.getenv('GROUP_ID'))  # Make sure GROUP_ID is an integer

# Logger settings
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher with MemoryStorage
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

conn, cur = setup_database()

# Define cursor object
c = conn.cursor()

# Create a PostgreSQL table to store user details
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        username TEXT,
        telegram_id INTEGER
    )
''')
conn.commit()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # Check if user already exists in the database
    user_exists = c.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,)).fetchone()

    # If user does not exist, insert their details into the database
    if not user_exists:
        c.execute('INSERT INTO users (full_name, username, telegram_id) VALUES (?, ?, ?)',
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


# Respond to admin's news
@dp.message_handler(state=News.waiting_for_news, content_types=types.ContentType.ANY)
async def handle_news(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        # Get all users from the database
        all_users = c.execute('SELECT telegram_id FROM users').fetchall()

        for user in all_users:
            try:
                await bot.copy_message(user, message.chat.id, message.message_id)
            except BotBlocked:
                logging.warning(f"Bot was blocked by the user {user}")
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

import os
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Initialize bot and dispatcher
bot_token = os.getenv('BOT_TOKEN')
if bot_token is None:
    raise ValueError("Missing BOT_TOKEN environment variable")
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

# Database credentials
dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')

# Connect to the PostgreSQL database
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor object
cur = conn.cursor()


# Define states for FSM
class Form(StatesGroup):
    login_id = State()
    password = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    try:
        # Check if telegram_id already exists in the database
        cur.execute("SELECT * FROM students WHERE telegram_id = %s", (message.from_user.id,))
        result = cur.fetchone()
        if result is None:
            await bot.send_message(message.chat.id,
                                   "Shaxsiy login raqamingizni yuboring.🇺🇿\n\nОтправьте свой личный номер для "
                                   "входа.🇷🇺\n\nSend your personal login number.🇬🇧")

            await Form.login_id.set()
        else:
            await bot.send_message(message.chat.id,
                                   "Siz allaqachon ro'yxatdan o'tgansiz!.🇺🇿\n\nВы уже зарегистрированы!🇷🇺\n\nYou "
                                   "are already"
                                   "registered!🇬🇧")
    except Exception as e:
        print(f"Error in cmd_start: {e}")


@dp.message_handler(state=Form.login_id)
async def process_login_id(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['login_id'] = message.text
        await bot.send_message(message.chat.id,
                               "Iltimos, parolingizni yuboring.🇺🇿\n\nОтправьте свой пароль.🇷🇺\n\nSend your password.🇬🇧")
        await Form.next()
    except Exception as e:
        print(f"Error in process_login_id: {e}")


@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['password'] = message.text
            # Check if login_id and password exist in the database
            cur.execute("SELECT * FROM students WHERE login_id = %s AND password = %s",
                        (data['login_id'], data['password']))
            result = cur.fetchone()
            if result is not None:
                # Update telegram_id in the database
                cur.execute("UPDATE students SET telegram_id = %s WHERE login_id = %s AND password = %s",
                            (message.from_user.id, data['login_id'], data['password']))
                conn.commit()
                await bot.send_message(message.chat.id,
                                       "Ro'xatdan o'tish muvaffaqiyatli amalga oshirildi!🇺🇿\n\nРегистрация прошла "
                                       "успешно!🇷🇺\n\nRegistration was successful!🇬🇧")
            else:
                await bot.send_message(message.chat.id,
                                       "Xatolik yuz berdi! Iltimos, qaytadan urinib ko'ring.🇺🇿\n\nПроизошла ошибка! "
                                       "Попробуйте еще раз.🇷🇺\n\nAn error occurred! Try again.🇬🇧\n\n/start")
        await state.finish()
    except Exception as e:
        print(f"Error in process_password: {e}")


@dp.message_handler(commands='register')
async def cmd_register(message: types.Message):
    try:
        # Check if the user is not already registered
        cur.execute("SELECT * FROM students WHERE telegram_id = %s", (message.from_user.id,))
        result = cur.fetchone()
        if result is None:
            await bot.send_message(message.chat.id,
                                   "Shaxsiy login raqamingizni yuboring.🇺🇿\n\nОтправьте свой личный номер для "
                                   "входа.🇷🇺\n\nSend your personal login number.🇬🇧")
            await Form.login_id.set()
        else:
            await bot.send_message(message.chat.id,
                                   "Siz allaqachon ro'yxatdan o'tgansiz! Shaxsiy login raqamingizni "
                                   "yuboring.🇺🇿\n\nВы уже"
                                   "зарегистрированы! Отправьте свой личный номер для входа.🇷🇺\n\nYou are already "
                                   "registered! Send your personal login number.🇬🇧")
            await Form.login_id.set()
    except Exception as e:
        print(f"Error in cmd_register: {e}")


@dp.message_handler(state=Form.login_id)
async def process_login_id(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['login_id'] = message.text
        await bot.send_message(message.chat.id,
                               "Iltimos, parolingizni yuboring.🇺🇿\n\nОтправьте свой пароль.🇷🇺\n\nSend your password.🇬🇧")
        await Form.next()
    except Exception as e:
        print(f"Error in process_login_id: {e}")


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(f"Error in polling: {e}")
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()

import os
import pytz
import psycopg2
import datetime
import aiocron
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from datetime import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv, find_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from psycopg2.extras import DictCursor

load_dotenv(find_dotenv())

bot_token = os.getenv('BOT_TOKEN')
if not bot_token:
    raise ValueError("Missing BOT_TOKEN environment variable")
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')

try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, cursor_factory=DictCursor)
    cur = conn.cursor()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
except psycopg2.OperationalError as e:
    print(f"Error in databasmain.pye connection: {e}")
    exit(1)


class Form(StatesGroup):
    login_id = State()
    password = State()
    teacher_rating = State()
    feedback = State()
    feedback_message = State()  # new state


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboards.add(types.KeyboardButton('Infoℹ⁉️'))
    await bot.send_message(message.chat.id, "👀", reply_markup=keyboards)

    try:
        cur.execute("SELECT * FROM students WHERE telegram_id = %s", (message.from_user.id,))
        result = cur.fetchone()
        if result is None:
            await bot.send_message(message.chat.id,
                                   "Shaxsiy login raqamingizni yuboring.")

            await Form.login_id.set()
        else:
            await bot.send_message(message.chat.id,
                                   "Siz allaqachon ro'yxatdan o'tgansiz!.")
    except Exception as es:
        print(f"Error occurred in cmd_start while starting the bot: {es}")


@dp.message_handler(state=Form.login_id)
async def process_login_id(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['login_id'] = message.text
        await bot.send_message(message.chat.id,
                               "Iltimos, parolingizni yuboring.")
        await Form.next()
    except Exception as es:
        print(f"Error occurred in process_login_id while processing login id: {es}")


@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['password'] = message.text
            cur.execute("SELECT * FROM students WHERE login_id = %s AND password = %s",
                        (data['login_id'], data['password']))
            result = cur.fetchone()
            if result is not None:
                cur.execute("UPDATE students SET telegram_id = %s WHERE login_id = %s AND password = %s",
                            (message.from_user.id, data['login_id'], data['password']))
                conn.commit()
                await bot.send_message(message.chat.id,
                                       "Ro'xatdan o'tish muvaffaqiyatli amalga oshirildi!")
            else:
                await bot.send_message(message.chat.id,
                                       "Xatolik yuz berdi! Iltimos, qaytadan urinib ko'ring. \n\n/start")
        await state.finish()
    except Exception as es:
        print(f"Error occurred in process_password while processing password: {es}")


@dp.message_handler(lambda message: message.text == 'Infoℹ⁉️')
async def handle_info_button(message: types.Message):
    try:
        cur.execute(
            "SELECT students.first_name, students.last_name, groups.group_num, students.course_num, "
            "students.telegram_id FROM students INNER JOIN groups ON students.group_id = groups.id WHERE "
            "students.telegram_id = %s",
            (message.from_user.id,))
        result = cur.fetchone()
        if result is not None:
            await bot.send_message(message.chat.id,
                                   f"Ism Familiya: ```{result[0]} {result[1]}```\n"
                                   f"Guruh raqami: ```{result[2]}```\n"
                                   f"Kurs: ```{result[3]}```\n"
                                   f"Telegram id: ```{result[4]}```", parse_mode='Markdown')
        else:
            await bot.send_message(message.chat.id,
                                   "Siz ro'yxatdan o'tmagansiz! Iltimos, /start buyrug'ini bosing.")
    except Exception as es:
        print(f"Error occurred in handle_info_button while handling info button: {es}")


# Define the inline keyboard
keyboard = InlineKeyboardMarkup()
keyboard.row(
    InlineKeyboardButton("1", callback_data="1"),
    InlineKeyboardButton("2", callback_data="2"),
    InlineKeyboardButton("3", callback_data="3"),
    InlineKeyboardButton("4", callback_data="4"),
    InlineKeyboardButton("5", callback_data="5")
)


@aiocron.crontab('* * * * *')
async def cronjob():
    now = datetime.now(pytz.timezone('Asia/Tashkent'))
    cur.execute("SELECT * FROM class_schedule WHERE day = %s AND end_time = %s",
                (now.weekday(), now.strftime('%H:%M:%S')))
    classes = cur.fetchall()
    for class_ in classes:
        cur.execute("SELECT telegram_id FROM students WHERE group_id = %s", (class_['group_id'],))
        students = cur.fetchall()
        for student in students:
            cur.execute("SELECT first_name, last_name FROM teachers WHERE id = %s", (class_['teacher_id'],))
            teacher = cur.fetchone()
            teacher_name = teacher['first_name'] + ' ' + teacher['last_name']

            cur.execute("SELECT name FROM lessons WHERE id = %s", (class_['lesson_id'],))
            lesson_name = cur.fetchone()['name']

            await bot.send_message(student['telegram_id'],
                                   f"📚 Fan: *{lesson_name}*\n"
                                   f"👨‍🏫 Ustoz: *{teacher_name}*\n"
                                   f"🚪Xona : *{class_['room']}*\n\n"
                                   "Ustozning pedagoglik mahoratiga baho bering❗️👇",
                                   reply_markup=keyboard, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data and c.data.isdigit())
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['score'] = int(callback_query.data)
        data['rating_message_id'] = callback_query.message.message_id  # Store the message ID

    feedback_message = await bot.send_message(callback_query.from_user.id, "Fikr mulohazalaringizni jo'nating")
    await Form.feedback_message.set()
    async with state.proxy() as data:
        data['feedback_prompt_message_id'] = feedback_message.message_id  # Store the message ID

    # Wait for 70 minutes
    await asyncio.sleep(70 * 60)

    # Check if the user has responded
    async with state.proxy() as data:
        if 'feedback' not in data:
            # If the user hasn't responded, delete the messages
            await bot.delete_message(callback_query.from_user.id, data['rating_message_id'])
            await bot.delete_message(callback_query.from_user.id, data['feedback_prompt_message_id'])


@dp.message_handler(state=Form.feedback_message)
async def process_feedback_message(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            cur.execute(
                "SELECT lesson_id, teacher_id FROM class_schedule WHERE group_id = (SELECT group_id FROM students "
                "WHERE telegram_id = %s)",
                (message.from_user.id,))
            lesson_id, teacher_id = cur.fetchone()

            cur.execute(
                "INSERT INTO scores (score_for_teacher, feedback, lesson_id, student_id, teacher_id, created_at, "
                "updated_at) VALUES (%s, %s, %s, (SELECT id FROM students WHERE telegram_id = %s), %s, NOW(), NOW())",
                (data['score'], message.text, lesson_id, message.from_user.id, teacher_id))
            conn.commit()

            # Delete the previous messages
            await bot.delete_message(message.chat.id, data['rating_message_id'])
            await bot.delete_message(message.chat.id, data['feedback_prompt_message_id'])

            await bot.send_message(message.chat.id, "Baholar qabul qilindi, E'tiboringiz uchun rahmat!👍")
        await state.finish()
    except Exception as es:
        print(f"Error in process_feedback_message: {es}")


if __name__ == '__main__':
    try:
        executor.start_polling(dp, timeout=60, skip_updates=True)
    except Exception as es:
        print(f"Error occurred in main while starting the bot: {es}")
    finally:
        cur.close()
        conn.close()

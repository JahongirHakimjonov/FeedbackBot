import os
import pytz
import psycopg2
import datetime
import aiocron
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv, find_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv(find_dotenv())

bot_token = os.getenv('BOT_TOKEN')
if not bot_token:
    raise ValueError("Missing BOT_TOKEN environment variable")
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()


class Form(StatesGroup):
    login_id = State()
    password = State()
    teacher_rating = State()
    feedback = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Infoℹ⁉️'))
    await bot.send_message(message.chat.id, "👀", reply_markup=keyboard)

    try:
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
            cur.execute("SELECT * FROM students WHERE login_id = %s AND password = %s",
                        (data['login_id'], data['password']))
            result = cur.fetchone()
            if result is not None:
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
                                   f"Ism, Name, Имя: {result[0]}\n"
                                   f"Familiya, Surname, Фамилия: {result[1]}\n"
                                   f"Guruh raqami, Group number, Номер группа: {result[2]}\n"
                                   f"Kurs, Course, Курс: {result[3]}\n"
                                   f"Telegram id: {result[4]}")
        else:
            pass
    except Exception as e:
        print(f"Error in handle_info_button: {e}")


@dp.message_handler(commands='rate_teacher')
async def cmd_rate_teacher(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=5)  # Set row_width to 5
    buttons = [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(1, 6)]
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, "Ustozning pedagoglik mahoratiga baho bering", reply_markup=keyboard)
    await Form.teacher_rating.set()


@dp.callback_query_handler(state=Form.teacher_rating)
async def process_teacher_rating(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['teacher_rating'] = int(call.data)
    await bot.send_message(call.from_user.id, "Fikr mulohazalaringizni jo'nating")
    await Form.next()


@dp.message_handler(state=Form.feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['feedback'] = message.text

        # Retrieve the current lesson's and teacher's IDs from the database
        cur.execute("SELECT group_id FROM students WHERE telegram_id = %s", (message.from_user.id,))
        result = cur.fetchone()
        if result is not None:
            group_id = result[0]

            cur.execute("SELECT lesson_id, day, end_time FROM class_schedule WHERE group_id = %s", (group_id,))
            result = cur.fetchone()
            if result is not None:
                current_lesson_id = result[0]
                day = result[1]
                end_time = result[2]

                # Convert end_time to a datetime object and add 80 minutes
                end_time = datetime.datetime.combine(datetime.date.today(),
                                                     datetime.datetime.strptime(end_time, '%H:%M').time())
                end_time = pytz.timezone('Asia/Tashkent').localize(
                    end_time)
                feedback_deadline = end_time + datetime.timedelta(minutes=80)

                now = datetime.datetime.now(
                    pytz.timezone('Asia/Tashkent'))
                if end_time <= now <= feedback_deadline:
                    print(f"Current lesson ID: {current_lesson_id}")
                    cur.execute("SELECT teacher_id FROM class_schedule_teacher WHERE classschedule_id = %s", (current_lesson_id,))
                    result = cur.fetchone()
                    if result is not None:
                        current_teacher_id = result[0]

                        created_at = datetime.datetime.now()
                        updated_at = created_at

                        cur.execute(
                            "INSERT INTO scores (lesson_id, student_id, teacher_id, score_for_teacher, feedback, "
                            "created_at, updated_at) VALUES (%s,"
                            "%s, %s, %s, %s, %s, %s)",
                            (current_lesson_id, message.from_user.id, current_teacher_id, data['teacher_rating'],
                             data['feedback'], created_at, updated_at))
                        conn.commit()
                    else:
                        await bot.send_message(message.chat.id, "Error: Could not retrieve the current teacher's ID.")
                else:
                    await bot.send_message(message.chat.id, "Feedback window has closed.")
            else:
                await bot.send_message(message.chat.id, "Error: Could not retrieve the current lesson's ID.")
        else:
            await bot.send_message(message.chat.id, "Error: Could not retrieve the group ID.")

    await bot.send_message(message.chat.id, "Rahmat! Sizning bahoingiz va fikr mulohazalaringiz qabul qilindi.")
    await state.finish()


async def send_rating_request():
    # Get the current date and time
    now = datetime.datetime.now(pytz.timezone('Asia/Tashkent'))

    # Subtract 80 minutes from the current time
    time_80_minutes_ago = now - datetime.timedelta(minutes=80)

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = now.weekday()

    # Fetch the lessons that ended 80 minutes ago
    cur.execute(
        "SELECT lesson_id, group_id FROM class_schedule WHERE CAST(day AS INTEGER) = %s AND CAST(end_time AS TIME) = %s",
        (day_of_week, time_80_minutes_ago.strftime('%H:%M'))
    )
    lessons = cur.fetchall()

    for lesson in lessons:
        # Fetch the students of the group
        cur.execute(
            "SELECT telegram_id FROM students WHERE group_id = %s",
            (lesson[1],)
        )
        students = cur.fetchall()

        for student in students:
            # Send the rating request to the student
            keyboard = InlineKeyboardMarkup(row_width=5)
            buttons = [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(1, 6)]
            keyboard.add(*buttons)
            await bot.send_message(student[0], "Ustozning pedagoglik mahoratiga baho bering", reply_markup=keyboard)


if __name__ == '__main__':
    try:
        # Schedule the send_rating_request task to run every minute
        aiocron.crontab('* * * * *', func=send_rating_request)

        executor.start_polling(dp, skip_updates=True, timeout=60)
    except Exception as e:
        print(f"Error in polling: {e}")
    finally:
        cur.close()
        conn.close()

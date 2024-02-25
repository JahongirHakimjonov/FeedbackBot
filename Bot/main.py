from aiogram import types
import logging
import os
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from states import Form
import aiocron
import pytz
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_setup import setup_bot
from setup import setup_database

bot, dp = setup_bot()

if __name__ == '__main__':

    bot, dp = setup_bot()
    conn, cur = setup_database()


    @dp.message_handler(commands='start')
    async def cmd_start(message: types.Message):
        keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
        await bot.send_message(message.chat.id, "Assalomu alaykum", reply_markup=keyboards)

        try:
            cur.execute("SELECT * FROM students WHERE telegram_id = %s", (message.from_user.id,))
            result = cur.fetchone()
            if result is None:
                await bot.send_message(message.chat.id, "*Shaxsiy login raqamingizni yuboring❗*", parse_mode='Markdown')
                await Form.login_id.set()
            else:
                await bot.send_message(message.chat.id, "*Siz allaqachon ro'yxatdan o'tgansiz❗*", parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in cmd_start while starting the bot: {es}")


    @dp.message_handler(state=Form.login_id)
    async def process_login_id(message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                data['login_id'] = message.text
            await bot.send_message(message.chat.id, "*Iltimos, parolingizni yuboring❗*", parse_mode='Markdown')
            await Form.next()
        except Exception as es:
            logging.error(f"Error occurred in process_login_id while processing login id: {es}")


    @dp.message_handler(state=Form.password)
    async def process_password(message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                data['password'] = message.text
                cur.execute("SELECT * FROM students WHERE login_id = %s AND password = %s",
                            (data['login_id'], data['password']))
                result = cur.fetchone()
                if result is not None:
                    if result['telegram_id'] is None:
                        cur.execute("UPDATE students SET telegram_id = %s WHERE login_id = %s AND password = %s",
                                    (message.from_user.id, data['login_id'], data['password']))
                        conn.commit()
                        await bot.send_message(message.chat.id, "*Ro'xatdan o'tish muvaffaqiyatli amalga oshirildi❗*",
                                               parse_mode='Markdown')
                    else:
                        await bot.send_message(message.chat.id, "*Bunday foydalanuvchi mavjud❗*\n\nQayta urunish uchun "
                                                                "/start "
                                                                "buyrug'ini bosing.", parse_mode='Markdown')
                else:
                    await bot.send_message(message.chat.id,
                                           "*ID yoki parolingiz xato iltimos qaytadan urunib ko'ring❗* \n\nQayta "
                                           "urunish"
                                           "uchun"
                                           " /start buyrug'ini bosing", parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in process_password while processing password: {es}")
        finally:
            await state.finish()


    @dp.message_handler(commands='about')
    async def cmd_info(message: types.Message):
        try:
            cur.execute(
                "SELECT students.first_name, students.last_name, groups.group_num, students.course_num, "
                "students.telegram_id FROM students INNER JOIN groups ON students.group_id = groups.id WHERE "
                "students.telegram_id = %s",
                (message.from_user.id,))
            result = cur.fetchone()
            if result is not None:
                await bot.send_message(message.chat.id,
                                       f"Ism: ```{result[0]}```\n"
                                       f"Familiya: ```{result[1]}```"
                                       f"Guruh raqami: ```{result[2]}```\n"
                                       f"Kurs: ```{result[3]}```\n"
                                       f"Telegram id: ```{result[4]}```", parse_mode='Markdown')
            else:
                await bot.send_message(message.chat.id,
                                       "*Siz ro'yxatdan o'tmagansiz❗* Iltimos, /start buyrug'ini bosing.",
                                       parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in cmd_info while handling info command: {es}")


    @dp.message_handler(commands='help')
    async def cmd_help(message: types.Message):
        try:
            await bot.send_message(message.chat.id,
                                   "Ushbu bot ta'lim sifatini nazorat qilish va ustozlarga baho berish uchun "
                                   "mo'ljallangan.\n"
                                   "Botdan foydalanish uchun quyidagi buyruqlardan foydalaning:\n\n"
                                   "/start - Botni ishga tushirish\n"
                                   "/about - O'z ma'lumotlaringizni ko'rish\n"
                                   "/tutorial - Botdan foydalanish uchun qo'llanma\n"
                                   "/help - Yordam\n\n"
                                   "*Bunday foydalanuvchi mavjud*\nhabari kelsa demak sizga tegishli ID va parol "
                                   "orqali boshqa talaba ro'yxatdan o'tgan bo'ladi. Bunday holatda siz fakultet "
                                   "dekanatiga murojat qilishingiz kerak.\n\n"
                                   "*ID yoki parolingiz xato iltimos qaytadan urunib ko'ring*\ndegan habar kelsa "
                                   "demak siz ID yoki parolni noto'g'ri kiritgansiz. Iltimos, qaytadan urinib "
                                   "ko'ring.\n\n"
                                   "*Ro'xatdan o'tish muvaffaqiyatli amalga oshirildi!*\nhabari kelgandagina siz "
                                   "ro'yxatdan muvafaqiyatli o'tgan bo'lasiz\n\n"
                                   "Darsingiz tugagan vaqtda 1 dan 5 gacha baho berish uchun habar keladi va "
                                   "baho berganingizdan so'ng\n\n*Dars va ustoz haqida fikr va takliflaringizni "
                                   "yuboring.*\n"
                                   "degan habar keladi bu holatda har qanday fikr va takliflaringizni "
                                   "yuborishingiz shart aks holda bergan bahoyingiz qabul qilinmaydi.❗",
                                   parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in cmd_help while handling help command: {es}")


    @dp.message_handler(commands='tutorial')
    async def cmd_tutorial(message: types.Message):
        try:
            # Send video with caption
            tutorial_video_path = os.path.join(os.path.dirname(__file__), '../media/tutorial.mp4')
            with open(tutorial_video_path, 'rb') as video_file:
                await bot.send_video(chat_id=message.chat.id, video=video_file,
                                     caption="Botdan foydalanish uchun ro'yxatdan o'tgan bo'lishingiz kerak.\n\n"
                                             "Ro'yxatdan o'tish uchun shaxsiy login raqamingizni yuboring. Bu sizning "
                                             "*HEMIS ID* raqamingiz hisoblanadi\n\n"
                                             "Keyingi qadamda parolingizni yuboring.\n\n"
                                             "Parol bu sizning passport seriya raqamingiz hisoblanadi.  Misol uchun: "
                                             "*AA1234567*\n\n"
                                             "Agar siz ro'yxatdan o'tgan "
                                             "bo'lsangiz, bot sizga ma'lumotlaringizni ko'rsatadi.\n\n"
                                             "Agar siz ro'yxatdan o'tmagan bo'lsangiz, bot sizni ro'yxatdan o'tishga "
                                             "chaqiradi.\n\n"
                                             "*Agar sizga darsingiz yo'q vaqtda baho berish uchun habar yuborilsa "
                                             "iltimos "
                                             "buni be'etibor qoldiring.❗️❗️*\n\n", parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in cmd_tutorial while handling tutorial command: {es}")


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
        conn, cur = setup_database()
        now = datetime.now(pytz.timezone('Asia/Tashkent'))
        cur.execute("SELECT * FROM class_schedule WHERE day = %s AND end_time = %s",
                    ((now.weekday() + 1) % 7, now.strftime('%H:%M:%S')))
        classes = cur.fetchall()
        for class_ in classes:
            cur.execute("SELECT telegram_id FROM students WHERE group_id = %s AND telegram_id IS NOT NULL",
                        (class_['group_id'],))
            students = cur.fetchall()
            for student in students:
                cur.execute("SELECT full_name FROM teachers WHERE id = %s", (class_['teacher_id'],))
                teacher_name = cur.fetchone()['full_name']

                cur.execute("SELECT name FROM lessons WHERE id = %s", (class_['lesson_id'],))
                lesson_name = cur.fetchone()['name']

                await bot.send_message(student['telegram_id'],
                                       f"📚 Fan: *{lesson_name}*\n"
                                       f"👨‍🏫 Ustoz: *{teacher_name}*\n"
                                       f"🚪Xona : *{class_['room']}*\n\n"
                                       "Ustozning pedagoglik mahoratiga baho bering❗👇",
                                       reply_markup=keyboard, parse_mode='Markdown')

                # Store the class_id in the state
                state = dp.current_state(user=student['telegram_id'])
                async with state.proxy() as data:
                    data['class_id'] = class_['id']


    @dp.callback_query_handler(lambda c: c.data and c.data.isdigit())
    async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['score'] = int(callback_query.data)
            data['rating_message_id'] = callback_query.message.message_id  # Store the message ID

        feedback_message = await bot.send_message(callback_query.from_user.id, "Dars va ustoz haqida fikr va "
                                                                               "takliflaringizni yuboring❗️",
                                                  parse_mode='Markdown')
        await Form.feedback_message.set()
        async with state.proxy() as data:
            data['feedback_prompt_message_id'] = feedback_message.message_id  # Store the message ID

        # Schedule the deletion of messages
        asyncio.create_task(delete_messages_after_delay(callback_query.from_user.id, data['rating_message_id'],
                                                        data['feedback_prompt_message_id'], 15 * 60))


    async def delete_messages_after_delay(user_id, rating_message_id, feedback_prompt_message_id, delay):
        await asyncio.sleep(delay)
        await bot.delete_message(user_id, rating_message_id)
        await bot.delete_message(user_id, feedback_prompt_message_id)


    @dp.message_handler(state=Form.feedback_message)
    async def process_feedback_message(message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                cur.execute(
                    "SELECT lesson_id, teacher_id FROM class_schedule WHERE id = %s",
                    (data['class_id'],))
                lesson_id, teacher_id = cur.fetchone()

                cur.execute(
                    "INSERT INTO scores (score_for_teacher, feedback, lesson_id, student_id, teacher_id, created_at, "
                    "updated_at) VALUES (%s, %s, %s, (SELECT id FROM students WHERE telegram_id = %s), %s, NOW(), "
                    "NOW())",
                    (data['score'], message.text, lesson_id, message.from_user.id, teacher_id))
                conn.commit()

                # Delete the previous messages
                await bot.delete_message(message.chat.id, data['rating_message_id'])
                await bot.delete_message(message.chat.id, data['feedback_prompt_message_id'])

                await bot.send_message(message.chat.id, "*Baholar qabul qilindi*, E'tiboringiz uchun rahmat!👍",
                                       parse_mode='Markdown')
            await state.finish()
        except Exception as es:
            print(f"Error in process_feedback_message: {es}")


    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.error(f"Error occurred: {e}")

from aiogram import types
import logging
import os
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

from states import Form
import aiocron
import pytz
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageToDeleteNotFound

from bot_setup import setup_bot
from setup import setup_database
from languages import english, russian, uzbek, japanese

bot, dp = setup_bot()

ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Make sure ADMIN_ID is an integer
GROUP_ID = int(os.getenv('GROUP_ID'))  # Make sure GROUP_ID is an integer

if __name__ == '__main__':

    bot, dp = setup_bot()
    conn, cur = setup_database()

    languages = {"Uzbek🇺🇿": uzbek, "English🇬🇧": english, "Russian🇷🇺": russian, "Japanese🇯🇵": japanese}


    @dp.message_handler(commands='lang')
    async def cmd_lang(message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        for language in languages.keys():
            keyboard.add(types.InlineKeyboardButton(language, callback_data=language))
        await bot.send_message(message.chat.id,
                               "Please choose a language🇬🇧\n\nIltimos tilni tanlang🇺🇿\n\nПожалуйста, выберите "
                               "язык🇷🇺\n\n言語を選択してください🇯🇵",
                               reply_markup=keyboard)


    @dp.callback_query_handler(lambda c: c.data and c.data in languages)
    async def process_language_callback(callback_query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['language'] = callback_query.data
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id,
                               f"You have chosen {callback_query.data} as your language.🇬🇧\n\nSiz {callback_query.data}"
                               f" tilini tanladingiz.🇺🇿\n\nВы выбрали {callback_query.data} в качестве вашего "
                               f"языка.🇷🇺\n\n言語として {callback_query.data} を選択しました。🇯🇵")
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


    async def send_message(user_id, message_key, state: FSMContext, parse_mode='Markdown'):
        async with state.proxy() as data:
            language = data.get('language', 'Uzbek🇺🇿')  # Default to Uzbek if no language is set
            message = languages[language][message_key]
            sent_message = await bot.send_message(user_id, message, parse_mode=parse_mode)
            if sent_message is None:
                raise Exception(f"Failed to send message: {message_key}")
            return sent_message


    @dp.message_handler(commands='start')
    async def cmd_start(message: types.Message, state: FSMContext):
        await send_message(message.chat.id, 'greeting', state)

        try:
            cur.execute("SELECT * FROM students WHERE telegram_id = %s", (message.from_user.id,))
            result = cur.fetchone()
            if result is None:
                await send_message(message.chat.id, 'login_prompt', state, parse_mode='Markdown')
                await Form.login_id.set()
            else:
                await send_message(message.chat.id, 'already_registered', state, parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in cmd_start while starting the bot: {es}")


    @dp.message_handler(state=Form.login_id)
    async def process_login_id(message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                data['login_id'] = message.text
            await send_message(message.chat.id, 'password_prompt', state, parse_mode='Markdown')
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
                        await send_message(message.chat.id, 'login_success', state,
                                           parse_mode='Markdown')
                    else:
                        await send_message(message.chat.id, 'user_exists', state, parse_mode='Markdown')
                else:
                    await send_message(message.chat.id, 'login_error', state, parse_mode='Markdown')
        except Exception as es:
            logging.error(f"Error occurred in process_password while processing password: {es}")
        finally:
            await state.finish()


    @dp.message_handler(commands='about')
    async def cmd_info(message: types.Message, state: FSMContext):
        try:
            cur.execute(
                "SELECT students.first_name, students.last_name, groups.group_num, students.course_num, "
                "students.telegram_id FROM students INNER JOIN groups ON students.group_id = groups.id WHERE "
                "students.telegram_id = %s",
                (message.from_user.id,))
            result = cur.fetchone()
            if result is not None:
                await bot.send_message(message.chat.id,
                                       f"Ism, Name, Имя: ```{result[0]}```\n"
                                       f"Familiya, Surname, Фамилия: ```{result[1]}```"
                                       f"Guruh, Group, Группа: ```{result[2]}```\n"
                                       f"Kurs, Course, Курс: ```{result[3]}```\n"
                                       f"Telegram ID: ```{result[4]}```", parse_mode='Markdown')
            else:
                await send_message(message.chat.id,
                                   'about_not_registered', state)
        except Exception as es:
            logging.error(f"Error occurred in cmd_info while handling info command: {es}")


    @dp.message_handler(commands='help')
    async def cmd_help(message: types.Message, state: FSMContext):
        try:
            await send_message(message.chat.id, 'help_message', state)
        except Exception as es:
            logging.error(f"Error occurred in cmd_help while handling help command: {es}")


    @dp.message_handler(commands='tutorial')
    async def cmd_tutorial(message: types.Message, state: FSMContext):
        try:
            # Define the caption
            sent_message = await send_message(message.chat.id, 'tutorial_message', state, parse_mode='Markdown')
            caption = sent_message.text
            await bot.delete_message(message.chat.id, sent_message.message_id)

            # Send video with caption
            tutorial_video_path = os.path.join(os.path.dirname(__file__), '../media/tutorial.mp4')
            with open(tutorial_video_path, 'rb') as video_file:
                await bot.send_video(chat_id=message.chat.id, video=video_file,
                                     caption=caption)
        except Exception as es:
            logging.error(f"Error occurred in cmd_tutorial while handling tutorial command: {es}")


    @dp.message_handler(commands=['news'])
    async def news_command(message: types.Message):
        if message.from_user.id == ADMIN_ID:
            await message.reply("Assalomu alaykum akajon habarizi yuboring man hammaga jo'nataman:")
            await Form.waiting_for_news.set()
        else:
            await message.reply("Adminmassizku nega bosvos uyatmasmi aaa?")


    @dp.message_handler(state=Form.waiting_for_news, content_types=types.ContentType.ANY)
    async def handle_news(message: types.Message, state: FSMContext):
        if message.from_user.id == ADMIN_ID:
            # Get all users from the database
            cur.execute('SELECT telegram_id FROM students WHERE telegram_id IS NOT NULL')
            users = cur.fetchall()

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
            await bot.send_message(ADMIN_ID, "Xabaringiz yuborildi.")
        else:
            await message.reply("Siz admin emassiz dib ettimu!!!")


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
        try:
            conn, cur = setup_database()
        except Exception as e:
            logging.error(f"Error occurred while setting up the database: {e}")
            return  # Exit the function

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

                try:
                    await bot.send_message(student['telegram_id'],
                                           f"📚 Fan, Lesson, Урок: *{lesson_name}*\n"
                                           f"👨‍🏫 Ustoz, Teacher, Преподаватель: *{teacher_name}*\n"
                                           f"🚪Xona, Room, Кабинет : *{class_['room']}*\n\n"
                                           "Ustozning pedagogik mahoratiga baho bering❗👇\n"
                                           "Rate the teacher's pedagogical skills❗👇\n"
                                           "Оцените педагогические навыки преподавателя❗👇",
                                           reply_markup=keyboard, parse_mode='Markdown')
                except BotBlocked:
                    logging.warning(f"Bot is blocked by the user: {student['telegram_id']}")

                try:
                    state = dp.current_state(user=student['telegram_id'])
                    async with state.proxy() as data:
                        data['class_id'] = class_['id']
                except Exception as e:
                    logging.error(f"Error occurred while setting the state: {e}")


    @dp.callback_query_handler(lambda c: c.data and c.data.isdigit())
    async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            # If there is a previous rating message, delete it
            if 'rating_message_id' in data:
                await bot.delete_message(callback_query.from_user.id, data['rating_message_id'])

            data['score'] = int(callback_query.data)
            data['rating_message_id'] = callback_query.message.message_id  # Store the new message ID

        feedback_message = await send_message(callback_query.from_user.id, "feedback_prompt", state,
                                              parse_mode='Markdown')
        await Form.feedback_message.set()
        async with state.proxy() as data:
            data['feedback_prompt_message_id'] = feedback_message.message_id  # Store the message ID

        # Schedule the deletion of messages after 5 minutes
        asyncio.create_task(delete_messages_after_delay(callback_query.from_user.id, data['rating_message_id'],
                                                        data['feedback_prompt_message_id'], 5 * 60))


    async def delete_messages_after_delay(user_id, rating_message_id, feedback_prompt_message_id, delay):
        await asyncio.sleep(delay)
        try:
            await bot.delete_message(user_id, rating_message_id)
        except MessageToDeleteNotFound:
            pass  # Message already deleted, do nothing
        try:
            await bot.delete_message(user_id, feedback_prompt_message_id)
        except MessageToDeleteNotFound:
            pass  # Message already deleted, do nothing


    @dp.message_handler(state=Form.feedback_message)
    async def process_feedback_message(message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                if 'class_id' not in data:
                    logging.error("class_id not found in data")
                    raise Exception("class_id not found in data")

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

                await send_message(message.chat.id, "finish_message", state, parse_mode='Markdown')
        except Exception as es:
            print(f"Error in process_feedback_message: {es}")
        finally:
            await state.finish()


    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    # finally:
    #     conn.close()
    #     cur.close()
    #     bot.close()

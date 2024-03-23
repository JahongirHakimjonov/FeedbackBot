import os
import logging
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated
from .bot_setup import setup_bot
from .setup import setup_database

bot, dp = setup_bot()
conn, cur = setup_database()


async def send_news():
    try:
        cur.execute("SELECT telegram_id FROM students WHERE telegram_id IS NOT NULL")
        users = cur.fetchall()
        cur.execute("SELECT title, content, image FROM news ORDER BY created_at DESC LIMIT 1")
        data = cur.fetchall()
        for user in users:
            for news in data:
                caption = f"*{news['title']}*\n\n{news['content']}"
                if len(caption) > 1024:
                    caption = caption[:1021] + "..."
                if news['image']:
                    try:
                        rasm = os.path.join(os.path.dirname(__file__), f"../media/{news['image']}")
                        with open(rasm, 'rb') as photo:
                            await bot.send_photo(user['telegram_id'], photo, caption=caption, parse_mode='Markdown')
                    except FileNotFoundError:
                        logging.error(f"File not found: media/{news['image']}")
                else:
                    await bot.send_message(user['telegram_id'], caption, parse_mode='Markdown')
    except BotBlocked:
        logging.warning(f"Bot was blocked by the user")
    except ChatNotFound:
        logging.error(f"Chat not found")
    except UserDeactivated:
        logging.warning(f"User deactivated the account")
    except Exception as es:
        logging.error(f"Error occurred in send_news: {es}")

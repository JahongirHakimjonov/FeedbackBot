import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.News.models import News
from Bot.main import send_news


@receiver(post_save, sender=News)
def news_post_save(sender, instance, created, **kwargs):
    if created:
        print("News created and sending to telegram ")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(send_news())
        finally:
            loop.close()

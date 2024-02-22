import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.News.models import News
from Bot.main import send_news


@receiver(post_save, sender=News)
async def news_post_save(sender, instance, created, **kwargs):
    if created:
        print("News created and sending to telegram ")
        await send_news()

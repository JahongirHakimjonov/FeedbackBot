import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.News.models import News
from Bot.main import send_news


@receiver(post_save, sender=News)
def news_post_save(sender, instance, created, **kwargs):
    if created:  # check if a new instance of News was created
        print("News created")

        # Create a new event loop and set it as the current event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the send_news function in the new event loop
            loop.run_until_complete(send_news())
        finally:
            # Close the event loop when you're done
            loop.close()

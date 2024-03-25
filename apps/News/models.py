from django.db import models

from apps.feedbackbot.models import AbstractBaseModel


class News(AbstractBaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="news", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "Yangilik va e'lonlar"
        db_table = "news"

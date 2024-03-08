from django.db import models


class SupportUsers(models.Model):
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name_plural = "Foydalanuvchilar"
        db_table = "support_user"


class DailyMessages(models.Model):
    telegram_id = models.BigIntegerField()
    message_date = models.DateField()
    message_count = models.IntegerField()

    def __str__(self):
        return f"{self.telegram_id}"

    class Meta:
        verbose_name_plural = "Kunlik xabarlar"
        db_table = "daily_message"

from django.contrib import admin

from apps.SupportBot.models import SupportUsers, DailyMessages


@admin.register(SupportUsers)
class SupportUsersAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'username', 'telegram_id')
    search_fields = ('full_name', 'username', 'telegram_id')


@admin.register(DailyMessages)
class DailyMessagesAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'message_count', 'message_date')

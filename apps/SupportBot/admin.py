from django.contrib import admin

from apps.SupportBot.models import SupportUsers, DailyMessages, AdminsID


@admin.register(SupportUsers)
class SupportUsersAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username", "telegram_id")
    search_fields = ("full_name", "username", "telegram_id")


@admin.register(DailyMessages)
class DailyMessagesAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "message_count", "message_date")


@admin.register(AdminsID)
class AdminsIDAdmin(admin.ModelAdmin):
    list_display = ("admin_id", "group_id")
    search_fields = ("admin_id", "group_id")

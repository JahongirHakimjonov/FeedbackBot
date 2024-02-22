from django.contrib import admin

from apps.News.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'image')
    search_fields = ('title', 'content')
    list_filter = ('title', 'content')
    list_per_page = 10
    list_max_show_all = 100


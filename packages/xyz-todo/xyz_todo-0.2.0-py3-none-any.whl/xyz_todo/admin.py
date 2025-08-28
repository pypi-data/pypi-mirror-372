from django.contrib import admin

from . import models


@admin.register(models.Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'name', 'title', 'user', 'is_done', 'expiration', 'update_time')
    list_filter = ('is_done', )
    raw_id_fields = ('user',)
    search_fields = ("name",)

from django.contrib import admin

from . import models


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'begin_time', 'end_time')
    raw_id_fields = ('user',)
    search_fields = ("title",)


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'user', 'survey')
    raw_id_fields = ('user', 'survey')

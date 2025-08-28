from django.contrib import admin

from . import models


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'category', 'create_time')
    raw_id_fields = ('category',)
    search_fields = ("name",)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'create_time')
    search_fields = ("name",)


@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_time')
    raw_id_fields = ('course',)

@admin.register(models.Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'is_pass', 'create_time')
    raw_id_fields = ('course', 'user')

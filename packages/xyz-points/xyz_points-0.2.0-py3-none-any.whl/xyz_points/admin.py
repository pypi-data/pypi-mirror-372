from django.contrib import admin

from . import models


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'create_time')

@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'is_active', 'coefficient', 'create_time')
    raw_id_fields = ('project', )

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'is_active', 'create_time')
    raw_id_fields = ('project', )

@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'number', 'is_active', 'begin_time', 'end_time', 'create_time')
    raw_id_fields = ('project', )

@admin.register(models.Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'session', 'category', 'value', 'create_time')
    raw_id_fields = ('project', 'session', 'user', 'category')
    search_fields = ('user__first_name',)

@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'point', 'owner_name', 'value', 'create_time')
    raw_id_fields = ('point', 'user')

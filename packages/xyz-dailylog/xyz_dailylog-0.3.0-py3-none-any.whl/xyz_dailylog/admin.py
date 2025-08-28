from django.contrib import admin

from . import models


@admin.register(models.DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'user', 'the_date')
    raw_id_fields = ('user',)

@admin.register(models.Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('the_date', 'owner_type', 'owner_id', 'metics', 'value', 'user_count')
    date_hierarchy = 'the_date'
    list_filter = ('owner_type', 'metics')

@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('the_date', 'owner_type', 'owner_id', 'metics', 'value', 'user')
    raw_id_fields = ('owner_type', 'user')
    readonly_fields = ('user',)
    date_hierarchy = 'the_date'
    list_filter = ('owner_type', 'metics')

@admin.register(models.Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('update_time', 'owner_type', 'owner_group', 'owner_name', 'user_name', 'owner_id', 'create_time')
    raw_id_fields = ('owner_type', 'user')
    search_fields = ('owner_name', 'user_name', 'owner_group')
    date_hierarchy = 'update_time'
    list_filter = ('owner_type', )
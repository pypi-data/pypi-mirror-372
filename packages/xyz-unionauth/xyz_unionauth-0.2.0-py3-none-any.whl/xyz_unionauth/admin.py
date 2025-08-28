from django.contrib import admin

from . import models

@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'procedure', 'landing_page', 'create_time')

@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('remote_id', 'source', 'name', 'is_active', 'user', 'create_time')
    raw_id_fields = ('source', 'user')

from django.contrib import admin
from .models import EduroamAccount
from apps.core.admin import BaseAccountAdmin

@admin.register(EduroamAccount)
class EduroamAdmin(BaseAccountAdmin):
    list_display = ('username', 'comment', 'owner', 'updated_at', 'status')
    search_fields = ('username', 'owner')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
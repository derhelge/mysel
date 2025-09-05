# apps/guests/admin.py
from django.contrib import admin
from .models import GuestAccount
from apps.core.admin import BaseAccountAdmin

@admin.register(GuestAccount)
class GuestAdmin(BaseAccountAdmin):
    list_display = ('name', 'username', 'owner', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'username',  'owner__username', 'owner__email', 'owner__first_name', 'owner__last_name')
    readonly_fields = ('created_at', 'updated_at')
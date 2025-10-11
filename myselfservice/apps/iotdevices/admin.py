from django.contrib import admin
from .models import IotDeviceAccount
from apps.core.admin import BaseAccountAdmin

@admin.register(IotDeviceAccount)
class IotDeviceAdmin(BaseAccountAdmin):
    list_display = ('device_name', 'mac_address', 'owner', 'updated_at', 'status')
    search_fields = ('device_name', 'mac_address', 'owner__username', 'owner__email', 'owner__first_name', 'owner__last_name')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
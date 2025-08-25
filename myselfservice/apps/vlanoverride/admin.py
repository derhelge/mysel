from django.contrib import admin
from .models import VlanOverride
from apps.core.admin import BaseAccountAdmin

@admin.register(VlanOverride)
class VlanOverrideAdmin(BaseAccountAdmin):
    list_display = ('mac_address', 'vlan_id', 'comment', 'updated_at', 'status')
    search_fields = ('mac_address','vlan_id', 'comment')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
from django.contrib import admin
from django.utils.html import format_html
from .models import FirewallRule, FirewallRuleChange


@admin.register(FirewallRule)
class FirewallRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'firewall_status', 'is_active', 'created_at')
    list_filter = ('is_active', 'remote_rule_status')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def firewall_status(self, obj):
        """Zeigt den Status der Firewall-Regel an"""
        if obj.remote_rule_status:
            return format_html('<span style="color: green;">✓ Aktiv</span>')
        return format_html('<span style="color: gray;">○ Inaktiv</span>')
    firewall_status.short_description = 'Firewall Status'


@admin.register(FirewallRuleChange)
class FirewallRuleChangeAdmin(admin.ModelAdmin):
    list_display = ('firewall_rule', 'user', 'action', 'api_status', 'created_at')
    list_filter = ('action', 'api_success')
    search_fields = ('firewall_rule__name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Änderungen werden nur durch die Anwendung erstellt
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit-Log soll nicht manuell bearbeitet werden
        return False
    
    def api_status(self, obj):
        """Zeigt den API-Status der Änderung an"""
        if obj.api_success:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    api_status.short_description = 'API'

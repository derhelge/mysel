from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
import uuid as uuid_lib
import logging

logger = logging.getLogger(__name__)


class FirewallRule(BaseModel):
    """Firewall-Regeln für verschiedene Räume/Bereiche"""
    
    uuid = models.UUIDField(
        unique=True,
        verbose_name='Firewall UUID',
        help_text='UUID der Regel in der OPNsense Firewall'
    )
    
    remote_rule_status = models.BooleanField(
        default=False, 
        verbose_name='Remote Status',
        help_text='Aktueller Status der Regel in der OPNsense Firewall'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Regelname',
        help_text='Beschreibender Name für die Firewall-Regel'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Beschreibung',
        help_text='Detaillierte Beschreibung des Zwecks dieser Regel'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktiv',
        help_text='Regel wird im Frontend angezeigt'
    )
    
    class Meta:
        verbose_name = 'Firewall-Regel'
        verbose_name_plural = 'Firewall-Regeln'
        permissions = [
            ("fwconfig_access", "Can manage firewall configuration"),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}"

class FirewallRuleChange(BaseModel):
    """Protokoll der Änderungen an Firewall-Regeln"""
    firewall_rule = models.ForeignKey(
        FirewallRule,
        on_delete=models.CASCADE,
        verbose_name='Firewall-Regel',
        related_name='changes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Benutzer'
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('enabled', 'eingeschaltet'),
            ('disabled', 'ausgeschaltet'),
        ],
        verbose_name='Aktion'
    )
    
    # API-Status der Änderung
    api_success = models.BooleanField(
        default=False,
        verbose_name='API erfolgreich',
        help_text='Wurde die Änderung erfolgreich an die Firewall übertragen?'
    )
    
    # API-Response/Fehlermeldung
    api_message = models.TextField(
        blank=True,
        verbose_name='API-Nachricht',
        help_text='Antwort oder Fehlermeldung von der Firewall-API'
    )
    
    class Meta:
        verbose_name = 'Firewall-Regel Änderung'
        verbose_name_plural = 'Firewall-Regel Änderungen'
        ordering = ['-created_at']
    
    def __str__(self):
        status_icon = '✓' if self.api_success else '✗'
        return f"{self.firewall_rule.name} - {self.get_action_display()} - {self.user.username} {status_icon}"

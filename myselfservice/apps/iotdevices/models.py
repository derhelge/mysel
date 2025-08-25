from django.conf import settings 
from django.db import models
from apps.core.models import BaseAccountModel

class IotDeviceAccount(BaseAccountModel):
    device_name = models.CharField(max_length=510, blank=True, verbose_name='Gerätename')
    username = None
    mac_address = models.CharField(
        max_length=17, 
        unique=False,
        verbose_name='MAC-Adresse'
        )
    class Meta:
        verbose_name = 'IoT Device Account'
        verbose_name_plural = 'IoT Device Accounts'
        permissions = [
            ("iotdevice_access", "Can manage IoT device accounts"),
        ]

    @classmethod
    def check_account_limit(cls, owner):
        """Prüft ob der Benutzer das Limit erreicht hat"""
        active_accounts = cls.objects.filter(
            owner=owner,
            status=cls.Status.ACTIVE
        ).count()
        return active_accounts < settings.IOTDEVICE_SETTINGS['MAX_ACCOUNTS']
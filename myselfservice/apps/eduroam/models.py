from django.conf import settings 
from django.db import models
from apps.core.models import BaseAccountModel
from django.utils.crypto import get_random_string

class EduroamAccount(BaseAccountModel):
    comment = models.CharField(max_length=510, blank=True, verbose_name='Kommentar')
    realm = models.CharField(max_length=510, default='thga.de', verbose_name='Realm')

    class Meta:
        verbose_name = 'Eduroam Account'
        verbose_name_plural = 'Eduroam Accounts'
        permissions = [
            ("eduroam_access", "Can manage eduroam accounts"),
        ]

    def _generate_unique_username(self, realm):
        """Generiert einen eindeutigen Username im Format eduXXXXX@realm"""
        while True:
            number = get_random_string(5, '0123456789')
            username = f'edu{number}@{realm}'
            if not EduroamAccount.objects.filter(username=username).exists():
                return username

    @classmethod
    def check_account_limit(cls, owner):
        """Prüft ob der Benutzer das Limit erreicht hat"""
        active_accounts = cls.objects.filter(
            owner=owner,
            status=cls.Status.ACTIVE
        ).count()
        return active_accounts < settings.EDUROAM_SETTINGS['MAX_ACCOUNTS']
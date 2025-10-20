from django.conf import settings 
from django.db import models
from apps.core.models import BaseAccountModel
import re
from django.core.exceptions import ValidationError

class VlanOverride(BaseAccountModel):
    username = None
    owner = None
    password = None
    mac_address = models.CharField(
        max_length=17, 
        unique=False,
        blank=True,
        null=True,
        verbose_name='MAC-Adresse'
        )
    
    wifi_username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='WLAN-Benutzername'
    )
    
    vlan_id = models.IntegerField(
        verbose_name='VLAN-ID',
        blank=False,
        null=False,
        help_text='Die VLAN-ID, die diesem Gerät zugewiesen werden soll.'
    )

    comment = models.CharField(
        max_length=510,
        blank=True,
        verbose_name='Kommentar'
    )
    
    def clean(self):
        super().clean()
        if not self.mac_address and not self.wifi_username:
            raise ValidationError('MAC-Adresse oder WLAN-Benutzername muss angegeben werden.')
        if self.mac_address:
            clean = re.sub(r'[^0-9A-F]', '', self.mac_address.upper())
            if len(clean) != 12:
                raise ValidationError({'mac_address': 'MAC-Adresse muss 12 Hex-Zeichen enthalten.'})
            self.mac_address = ':'.join([clean[i:i+2] for i in range(0, 12, 2)])

    class Meta:
        verbose_name = 'VLAN Override'
        verbose_name_plural = 'VLAN Overrides'

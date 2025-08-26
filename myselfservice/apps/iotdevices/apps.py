from django.apps import AppConfig
from apps.core.replication import replication_registry

class IotdevicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.iotdevices'
    verbose_name = 'IoT Devices'

    nav_config = {
        'title': 'IoT-Geräte',
        'icon': 'fas fa-microchip',
        'url_name': 'iotdevices:list',
        'permission': 'iotdevices.iotdevice_access',
        'description': 'Verwalten Sie hier Ihre IoT-Gerätekonten und erstellen Sie neue Zugänge.',
        'order': 30, 
    }
    def ready(self):
        replication_registry.register_table('iotdevices_iotdeviceaccount')
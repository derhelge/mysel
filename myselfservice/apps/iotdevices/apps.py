from django.apps import AppConfig

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
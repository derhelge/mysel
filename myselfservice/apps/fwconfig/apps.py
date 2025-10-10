from django.apps import AppConfig
from apps.core.replication import replication_registry


class FwconfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fwconfig"
    verbose_name = 'FWConfig'

    nav_config = {
        'title': 'Firewall Konfiguration',
        'icon': 'fas fa-trowel-bricks',
        'url_name': 'fwconfig:list',
        'permission': 'fwconfig.fwconfig_access',
        'description': 'Verwalten Sie hier die Firewall-Konfiguration.',
        'order': 50,
    }

from django.apps import AppConfig
from apps.core.replication import replication_registry

class VlanoverrideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vlanoverride'
    verbose_name = 'VLAN Overrides'

    def ready(self):
        replication_registry.register_table('vlanoverride_vlanoverride')
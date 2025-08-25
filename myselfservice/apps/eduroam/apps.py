from django.apps import AppConfig
from apps.core.replication import replication_registry

class EduroamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.eduroam'
    verbose_name = 'Eduroam'
    
    nav_config = {
        'title': 'Eduroam',
        'icon': 'fas fa-wifi',
        'url_name': 'eduroam:list',
        'permission': 'eduroam.eduroam_access',
        'description': 'Verwalten Sie hier Ihre Eduroam-Gerätekonten und erstellen Sie neue Zugänge.',
        'order': 10, 
    }
    def ready(self):
        import apps.eduroam.signals
        replication_registry.register_table('eduroam_eduroamaccount')
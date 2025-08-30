from django.apps import AppConfig
from apps.core.replication import replication_registry


class GuestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.guests"
    verbose_name = 'Guests'

    nav_config = {
        'title': 'Gäste',
        'icon': 'fas fa-users',
        'url_name': 'guests:list',
        'permission': 'guests.sponsoring_access',
        'description': 'Verwalten Sie hier Ihre Gast-Zugänge und genehmigen Sie neue Anträge.',
        'order': 40,
    }

    def ready(self):
        import apps.guests.signals
        replication_registry.register_table('guests_guestaccount')
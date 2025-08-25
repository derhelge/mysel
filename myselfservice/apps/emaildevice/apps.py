from django.apps import AppConfig


class EmailDeviceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.emaildevice"
    verbose_name = 'EmailDevice'

    nav_config = {
        'title': 'Mail-Accounts',
        'icon': 'fas fa-envelope',
        'url_name': 'emaildevice:list',
        'permission': 'emaildevice.emaildevice_access',
        'description': 'Verwalten Sie hier Mail-Accounts und erstellen Sie individuelle Accounts für Geräte.',
        'order': 20,
    }
from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"
    verbose_name = 'Events'
    
    nav_config = {
        'title': 'Events',
        'icon': 'fas fa-calendar',
        'url_name': 'events:list',
        'permission': 'events.events_access',
        'description': 'Verwalten Sie hier Events und erstellen Sie individuelle Accounts für Events.',
        'order': 50,
    }
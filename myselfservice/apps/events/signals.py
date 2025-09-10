from django.db.models.signals import post_save
from django.dispatch import receiver
from core.utils import send_admin_notification
from .models import Event

@receiver(post_save, sender=Event)
def event_saved(sender, instance, created, **kwargs):
    action = 'erstellt' if created else 'geändert'
    send_admin_notification(instance, action)

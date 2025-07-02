# apps/events/management/commands/cleanup_events.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.events.models import Event

class Command(BaseCommand):
    help = 'Cleanup expired events und event accounts'

    def handle(self, *args, **options):
        expired_events = Event.objects.filter(
            end_date__lt=timezone.now() - timezone.timedelta(days=14)
        )
        count = 0
        for event in expired_events:
            count += 1
            self.stdout.write(
                f'Setting event to DELETED: {event.name}'
            )
            event.delete()
            
        self.stdout.write(f'Cleaned up {count} expired events')

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from apps.eduroam.models import EduroamAccount
import csv

User = get_user_model()

class Command(BaseCommand):
    help = 'Import legacy eduroam accounts from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        # Status mapping from legacy to new system
        status_map = {
            '0': EduroamAccount.Status.ACTIVE,
            '-1': EduroamAccount.Status.DELETED
        }

        with open(options['csv_file']) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                # Skip deleted accounts
                if row['status'] == '-1':
                    continue

                # Get or create user
                owner, _ = User.objects.get_or_create(
                    username=row['owner_uid'].lower(),
                )
                
                # Create eduroam account with mapped status
                EduroamAccount.objects.create(
                    username=row['username'],
                    password=row['password'],
                    owner=owner,
                    status=status_map[row['status']],
                    realm=row['realm'],
                    comment=row['comment'],
                    created_at=now(),
                    updated_at=now()
                )
                
                self.stdout.write(f"Imported {row['username']}")
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from apps.eduroam.models import EduroamAccount
import csv
import logging

logger = logging.getLogger(__name__)

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

        imported_count = 0
        skipped_count = 0

        with open(options['csv_file']) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                try:
                    if row['status'] == '-1':
                        logger.debug(f"Skipped deleted account: {row['username']}")
                        skipped_count += 1
                        continue

                    _owner = row['owner_uid'].lower()

                    existing_account = EduroamAccount.objects.filter(
                        username=row['username'],
                    ).first()
                    
                    if existing_account:
                        logger.warning(f"Account already exists, skipping: {row['username']}")
                        skipped_count += 1
                        continue

                    owner, created = User.objects.get_or_create(
                        username=_owner,
                    )
                    if created:
                        logger.info(f"Created new user: {owner.username}")
                    else:
                        logger.debug(f"User already exists: {owner.username}")

                    account = EduroamAccount.objects.create(
                        username=row['username'],
                        password=row['password'],
                        owner=owner,
                        status=status_map[row['status']],
                        realm=row['realm'],
                        comment=row['comment'],
                        created_at=now(),
                        updated_at=now()
                    )

                    logger.info(f"Imported {account.username}")
                    imported_count += 1

                except Exception as e:
                    logger.error(f"Failed to import row with username {row.get('username', 'unknown')}: {str(e)}")
                    continue

        logger.info(f"Import completed. Imported: {imported_count}, Skipped: {skipped_count}")
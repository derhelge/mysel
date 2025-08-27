from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from apps.iotdevices.models import IotDeviceAccount
import csv
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class Command(BaseCommand):
    help = 'Import legacy IotDevice accounts from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        # Status mapping from legacy to new system
        status_map = {
            '1': IotDeviceAccount.Status.ACTIVE,
            '0': IotDeviceAccount.Status.DELETED
        }

        imported_count = 0
        skipped_count = 0

        with open(options['csv_file']) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                try:
                    if row['status'] == '0':
                        logger.info(f"Skipped deleted account: {row['mac_address']}")
                        skipped_count += 1
                        continue
                    _username = row['username'].lower()

                    existing_account = IotDeviceAccount.objects.filter(
                        owner__username=_username,
                        password=row['password'],
                        mac_address=row['mac_address']
                    ).first()
                    
                    if existing_account:
                        logger.warning(f"Account already exists, skipping: {row['mac_address']}")
                        skipped_count += 1
                        continue

                    owner, created = User.objects.get_or_create(
                        username=_username,
                    )
                    if created:
                        logger.info(f"Created new user: {owner.username}")
                    else:
                        logger.info(f"User already exists: {owner.username}")

                    account = IotDeviceAccount.objects.create(
                        mac_address=row['mac_address'],
                        password=row['password'],
                        owner=owner,
                        status=status_map[row['status']],
                        device_name=row['device_name'],
                        created_at=now(),
                        updated_at=now()
                    )

                    logger.info(f"Imported MAC-Address {account.mac_address}: {account.device_name}")
                    imported_count += 1

                except Exception as e:
                    logger.error(f"Failed to import row with MAC {row.get('mac_address', 'unknown')}: {str(e)}")
                    continue

        logger.info(f"Import completed. Imported: {imported_count}, Skipped: {skipped_count}")
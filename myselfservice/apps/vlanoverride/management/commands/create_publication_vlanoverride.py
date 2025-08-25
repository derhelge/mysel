# eduroam/management/commands/create_publication_eduroamaccount.py
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates the replication publication for table vlanoverride_vlanoverride'

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                # Check if publication exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_publication WHERE pubname = 'vlanoverride_pub'
                    );
                """)
                exists = cursor.fetchone()[0]
                
                if not exists:
                    cursor.execute("""
                        CREATE PUBLICATION vlanoverride_pub FOR TABLE vlanoverride_vlanoverride;
                        GRANT ALL ON vlanoverride_vlanoverride TO replicator;
                        GRANT USAGE ON SCHEMA public TO replicator;
                    """)
                    logger.info('Successfully created publication vlanoverride_pub')
                else:
                    logger.info('Publication vlanoverride_pub already exists')
        except Exception as e:
            logger.error(f'Failed to create/check publication: {str(e)}')
            raise
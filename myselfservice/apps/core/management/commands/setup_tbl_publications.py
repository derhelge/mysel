from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from apps.core.replication import replication_registry
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates a publication for all registered tables'

    def handle(self, *args, **options):
        tables = replication_registry.get_tables()
        pub_name = "all_tables_pub"

        logger.info(f'Starting publication creation for {len(tables)} tables')

        with connection.cursor() as cursor:
            # Check if publication exists
            cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = %s);", [pub_name])
            if cursor.fetchone()[0]:
                logger.info(f'{pub_name} already exists')
            else:
                table_list = ', '.join(tables)
                logger.debug(f"CREATE PUBLICATION {pub_name} FOR TABLE {table_list};")
                cursor.execute(f"CREATE PUBLICATION {pub_name} FOR TABLE {table_list};")
                for table in tables:
                    logger.debug(f"GRANT ALL ON {table} TO {settings.POSTGRES_REPLICATION_USER};")
                    cursor.execute(f"GRANT ALL ON {table} TO {settings.POSTGRES_REPLICATION_USER};")
                logger.info(f'Created {pub_name} for tables: {table_list}')

        logger.info('Publication creation completed')
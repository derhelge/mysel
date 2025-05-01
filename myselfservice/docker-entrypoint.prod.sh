#!/bin/bash
set -e

# Migrationen ausführen
python manage.py migrate


python manage.py collectstatic --noinput

# Superuser erstellen (nur wenn noch keiner existiert)
if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(User.objects.filter(is_superuser=True).exists())"; then
    python manage.py createsuperuser --noinput
fi

exec "$@"
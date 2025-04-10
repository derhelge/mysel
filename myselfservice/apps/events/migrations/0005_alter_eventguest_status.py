# Generated by Django 5.1.3 on 2025-01-18 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_alter_event_nameprefix"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventguest",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "Unbestätigt"),
                    (1, "Aktiv"),
                    (2, "Gebannt"),
                    (-1, "Gelöscht"),
                    (-2, "Endgültig gelöscht"),
                ],
                default=1,
                verbose_name="Status",
            ),
        ),
    ]

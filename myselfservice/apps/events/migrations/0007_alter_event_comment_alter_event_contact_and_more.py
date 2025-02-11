# Generated by Django 5.1.3 on 2025-01-21 09:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0006_alter_event_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="comment",
            field=models.TextField(blank=True, verbose_name="Kommentar (optional)"),
        ),
        migrations.AlterField(
            model_name="event",
            name="contact",
            field=models.EmailField(
                max_length=254, verbose_name="Kontakt Email-Adresse"
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="description",
            field=models.TextField(blank=True, verbose_name="Beschreibung (optional)"),
        ),
        migrations.AlterField(
            model_name="event",
            name="name",
            field=models.CharField(
                max_length=510,
                validators=[django.core.validators.MinLengthValidator(3)],
                verbose_name="Name der Veranstaltung",
            ),
        ),
    ]

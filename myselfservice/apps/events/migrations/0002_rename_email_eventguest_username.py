# Generated by Django 5.1.3 on 2024-12-14 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="eventguest",
            old_name="email",
            new_name="username",
        ),
    ]

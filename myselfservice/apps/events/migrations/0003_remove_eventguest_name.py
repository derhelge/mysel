# Generated by Django 5.1.3 on 2024-12-18 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_rename_email_eventguest_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventguest",
            name="name",
        ),
    ]

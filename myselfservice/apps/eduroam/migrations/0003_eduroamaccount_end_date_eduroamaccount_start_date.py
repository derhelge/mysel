# Generated by Django 5.1.3 on 2024-12-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eduroam", "0002_alter_eduroamaccount_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="eduroamaccount",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Enddatum"),
        ),
        migrations.AddField(
            model_name="eduroamaccount",
            name="start_date",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Startdatum"
            ),
        ),
    ]

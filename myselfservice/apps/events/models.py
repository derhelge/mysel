import random
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator,MaxLengthValidator, MaxValueValidator, RegexValidator
from apps.core.models import BaseModel, BaseAccountModel
from django.utils import timezone

from apps.core.utils import generate_password 

class AccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status=BaseAccountModel.Status.HARD_DELETED)

class AdminAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
class Event(BaseModel):
    objects = AccountManager()
    all_objects = AdminAccountManager()
    class Status:
        PENDING = 0
        ACTIVE = 1
        BANNED = 2
        DELETED = -1
        HARD_DELETED = -2

    STATUS_CHOICES = [
        (Status.PENDING, 'Unbestätigt'),
        (Status.ACTIVE, 'Aktiv'),
        (Status.BANNED, 'Gebannt'),
        (Status.DELETED, 'Gelöscht'),
        (Status.HARD_DELETED, 'Endgültig gelöscht'),
    ]

    name = models.CharField(
        max_length=510,
        validators=[MinLengthValidator(3)],
        verbose_name='Name der Veranstaltung'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Beschreibung (optional)'
    )
    contact = models.EmailField(
        verbose_name='Kontakt Email-Adresse'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events',
        verbose_name='Ersteller'
    )
    start_date = models.DateField(verbose_name='Startdatum')
    end_date = models.DateField(verbose_name='Enddatum')
    comment = models.TextField(blank=True, verbose_name='Kommentar (optional)')
    number = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(settings.EVENT_SETTINGS['MAX_ACCOUNTS'])
        ],
        verbose_name='Anzahl Accounts'
    )

    nameprefix = models.CharField(
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_\-]+$',
                message='Prefix darf nur Buchstaben, Zahlen und die Zeichen "_-" enthalten'
            ),
            MinLengthValidator(2),
            MaxLengthValidator(10)
        ],
        verbose_name='Prefix'
    )
    seed = models.CharField(
        max_length=510,
        blank=True,
        verbose_name='Seed für Passwörter'
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=Status.ACTIVE,
        verbose_name='Status'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Veranstaltung'
        verbose_name_plural = 'Veranstaltungen'
        permissions = [("events_access", "Can manage events")]

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property 
    def is_banned(self):
        return self.status == self.Status.BANNED

    @property
    def is_deleted(self):
        return self.status == self.Status.DELETED

    def ban(self):
        """Sperrt die Veranstaltung"""
        self.status = self.Status.BANNED
        self.save()

    def delete(self):
        """Löscht die Veranstaltung und alle Accounts (soft delete)"""
        self.status = self.Status.DELETED
        self.guests.all().update(status=self.Status.DELETED)
        self.save()

    def update_guests(self):
        """Synchronisiert alle EventGuest-Accounts mit aktuellen Event-Daten"""

        update_fields = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status
        }
        
        self.guests.all().update(**update_fields)

    def generate_accounts(self):
        """Generiert die Accounts für die Veranstaltung"""
        if self.guests.count() > 0:
            return False

        # Wenn seed gesetzt, nutze deterministischen Generator
        if self.seed:
            random.seed(self.seed)

        for i in range(self.number):
            # Username generieren: prefix + laufende Nummer
            username = f"{self.nameprefix}{i+1:03d}"
            
            # Passwort generieren
            password = generate_password()

            EventGuest.objects.create(
                event=self,
                username=f"{username}@event.local",
                password=password,
                owner=self.creator,
                start_date=self.start_date,
                end_date=self.end_date
            )

        return True

class EventGuest(BaseAccountModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='guests',
        verbose_name='Veranstaltung'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Veranstaltungsgast'
        verbose_name_plural = 'Veranstaltungsgäste'

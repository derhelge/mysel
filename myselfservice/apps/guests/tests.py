# apps/guests/tests.py
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import GuestAccount
from django.core import mail
from django.test import override_settings

User = get_user_model()

class GuestAccountModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        
    def test_guest_account_creation(self):
        guest = GuestAccount.objects.create(
            name='Test Guest',
            username='guest@example.com',
            owner=self.owner,
            duration=7
        )
        self.assertTrue(guest.password)
        self.assertEqual(guest.status, GuestAccount.Status.ACTIVE)
        self.assertIsNotNone(guest.start_date)
        self.assertIsNotNone(guest.end_date)
        
    def test_guest_account_extension(self):
        guest = GuestAccount.objects.create(
            name='Test Guest',
            username='guest@example.com',
            owner=self.owner
        )
        original_end_date = guest.end_date
        guest.extend(duration=14)
        self.assertGreater(guest.end_date, original_end_date)
        self.assertEqual(guest.extension_count, 1)
        
    def test_guest_account_limit(self):
        # Test maximum number of active guests per owner
        for i in range(6):  # Trying to create one more than limit
            GuestAccount.objects.create(
                name=f'Test Guest {i}',
                username=f'guest{i}@example.com',
                owner=self.owner
            )
        self.assertFalse(GuestAccount.can_owner_more(self.owner))

class GuestAccountViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Permission
        self.client = Client()
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        perm = Permission.objects.get(codename='sponsoring_access')
        self.owner.user_permissions.add(perm)
        self.client.login(username='testowner', password='testpass123')
        
    def test_guest_list_view(self):
        response = self.client.get(reverse('guests:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guests/guest_list.html')

    def test_guest_list_displays_active_guest_password(self):
        guest = GuestAccount.objects.create(
            name='Visible Guest',
            username='visible@example.com',
            owner=self.owner,
            password='visible-password'
        )

        response = self.client.get(reverse('guests:list'))

        self.assertContains(response, guest.password)
        
    def test_guest_create_view(self):
        data = {
            'name': 'New Guest',
            'username': 'newguest@example.com',
            'duration': 7,
            'message': 'Test message'
        }
        response = self.client.post(reverse('guests:create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(GuestAccount.objects.filter(username='newguest@example.com').exists())

    @override_settings(FRC_CAPTCHA_MOCKED_VALUE=True)
    def test_guest_application_process(self):
        # applicate ist das oeffentliche Formular - eingeloggte User werden umgeleitet
        self.client.logout()
        data = {
            'name': 'Applicant Guest',
            'username': 'applicant@example.com',
            'owner_email': self.owner.email,
            'duration': 7,
            'message': 'Please approve',
            'captcha': 'mocked_captcha_key',
        }
        response = self.client.post(reverse('guests:applicate'), data)
        self.assertEqual(len(mail.outbox), 2)  # Check notification email
        guest = GuestAccount.objects.get(username='applicant@example.com')
        self.assertEqual(guest.status, GuestAccount.Status.PENDING)

class GuestAccountCleanupTests(TestCase):
    def test_cleanup_command(self):
        owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        
        # Create expired guest account
        expired_guest = GuestAccount.objects.create(
            name='Expired Guest',
            username='expired@example.com',
            owner=owner,
            end_date=timezone.now() - timedelta(days=15)
        )
        
        from django.core.management import call_command
        call_command('cleanup_guests')
        
        expired_guest.refresh_from_db()
        self.assertEqual(expired_guest.status, GuestAccount.Status.HARD_DELETED)


class GuestAccountStatusTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.guest = GuestAccount.objects.create(
            name='Test Guest',
            username='guest@example.com',
            owner=self.owner,
            duration=7
        )

    def test_status_transitions(self):
        """Test alle erlaubten Status-Übergänge"""
        # Test Ban
        self.guest.ban()
        self.assertTrue(self.guest.is_banned)
        
        # Test Soft Delete
        self.guest.delete()
        self.assertTrue(self.guest.is_deleted)
        
        # Test Reactivation
        self.guest.reactivate()
        self.assertTrue(self.guest.is_active)
        
        # Test Hard Delete (should not be visible to normal users)
        self.guest.hard_delete()
        self.assertFalse(GuestAccount.objects.filter(id=self.guest.id).exists())
        self.assertTrue(GuestAccount.all_objects.get(id=self.guest.id).status == GuestAccount.Status.HARD_DELETED)

    def test_extension_limits(self):
        """Test Verlängerungslimits"""
        for i in range(settings.GUEST_SETTINGS['LIMIT_EXTEND_GUEST']):
            self.guest.extend()
        
        with self.assertRaises(Exception):
            self.guest.extend()

class GuestAccountNotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.guest = GuestAccount.objects.create(
            name='Test Guest',
            username='guest@example.com',
            owner=self.owner,
            duration=7
        )

    def test_activation_notification(self):
        """Test Aktivierungsbenachrichtigung"""
        from apps.guests.utils import send_guest_notification
        send_guest_notification(self.guest, 'activate')
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('aktiviert', mail.outbox[0].subject)
        self.assertIn(self.guest.username, mail.outbox[0].body)
        self.assertIn(self.guest.password, mail.outbox[0].body)

    def test_owner_notification_for_application(self):
        """Test Benachrichtigung an Owner bei neuer Anfrage"""
        from apps.guests.utils import send_owner_notification
        self.guest.status = GuestAccount.Status.PENDING
        self.guest.save()
        
        send_owner_notification(self.guest)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Antrag', mail.outbox[0].subject)
        self.assertIn(str(self.guest.id), mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to[0], self.owner.email)

class GuestAccountEdgeCaseTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )

    def test_duplicate_email_prevention(self):
        """Test Verhinderung doppelter E-Mail-Adressen"""
        GuestAccount.objects.create(
            name='First Guest',
            username='duplicate@example.com',
            owner=self.owner
        )
        
        with self.assertRaises(Exception):
            GuestAccount.objects.create(
                name='Second Guest',
                username='duplicate@example.com',
                owner=self.owner
            )

    def test_expired_account_handling(self):
        """Test Handling abgelaufener Accounts"""
        guest = GuestAccount.objects.create(
            name='Expired Guest',
            username='expired@example.com',
            owner=self.owner,
            end_date=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(guest.is_expired)
        
        # Teste Reaktivierung
        guest.reactivate()
        self.assertFalse(guest.is_expired)
        self.assertTrue(guest.is_active)

    def test_owner_limit_enforcement(self):
        """Test Durchsetzung der Owner-Limits"""
        # Erstelle maximum erlaubte Anzahl
        for i in range(settings.GUEST_SETTINGS['LIMIT_ACTIVE_GUESTS']):
            GuestAccount.objects.create(
                name=f'Guest {i}',
                username=f'guest{i}@example.com',
                owner=self.owner
            )
            
        # Versuche einen weiteren zu erstellen
        with self.assertRaises(Exception):
            guest = GuestAccount.objects.create(
                name='One Too Many',
                username='toomany@example.com',
                owner=self.owner
            )
            guest.activate()

class GuestFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testowner', password='testpass123')
    @override_settings(FRC_CAPTCHA_MOCKED_VALUE=True)
    def test_guest_application_form_validation(self):
        """Test Validierung des Antragsformulars"""
        from apps.guests.forms import GuestApplicationForm
        
        # Test mit invalider Owner-Email
        data = {
            'name': 'Test Guest',
            'username': 'newguest@example.com',
            'owner_email': 'non-existent@example.com',
            'message': 'Test message',
            'duration': 7,
            'captcha': 'mocked_captcha_key',
        }
        form = GuestApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('owner_email', form.errors)

    @override_settings(FRC_CAPTCHA_MOCKED_VALUE=True)
    def test_duration_validation(self):
        """Test Validierung der Zugangsdauer"""
        self.client.logout()
        data = {
            'name': 'Test Guest',
            'username': 'newguest@example.com',
            'owner_email': self.owner.email,
            'duration': 999,  # Ungültige Dauer
            'message': 'Test message',
            'captcha': 'mocked_captcha_key',
        }
        response = self.client.post(reverse('guests:applicate'), data)
        self.assertEqual(response.status_code, 200)  # Bleibt auf der Formularseite
        self.assertIn('duration', response.context['form'].errors)

class GuestAccountCleanupAndPrivacyTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        
    def test_automatic_cleanup(self):
        """Test automatische Bereinigung alter Accounts"""
        from django.core.management import call_command
        # Erstelle verschiedene Test-Accounts
        expired_old = GuestAccount.objects.create(
            name='Old Expired',
            username='oldexpired@example.com',
            owner=self.owner,
            end_date=timezone.now() - timedelta(days=15)
        )
        
        expired_recent = GuestAccount.objects.create(
            name='Recent Expired',
            username='recentexpired@example.com',
            owner=self.owner,
            end_date=timezone.now() - timedelta(days=7)
        )
        
        # Führe Cleanup durch
        call_command('cleanup_guests')

        # Überprüfe Ergebnisse (mit anderem Manager all_objects statt objects)
        self.assertEqual(
            GuestAccount.all_objects.get(id=expired_old.id).status,
            GuestAccount.Status.HARD_DELETED
        )
        self.assertNotEqual(
            GuestAccount.all_objects.get(id=expired_recent.id).status,
            GuestAccount.Status.HARD_DELETED
        )

    def test_privacy_data_handling(self):
        """Test Datenschutz-konformes Handling von Benutzerinformationen"""
        guest = GuestAccount.objects.create(
            name='Privacy Test',
            username='privacy@example.com',
            owner=self.owner
        )
        
        original_username = guest.username
        
        # Test Hard Delete
        guest.hard_delete()
        guest.refresh_from_db()
        
        # Prüfe ob Username verschleiert wurde
        self.assertNotEqual(guest.username, original_username)
        self.assertTrue(guest.username.startswith('deleted_'))
        self.assertIn(str(guest.id), guest.username)

class GuestAccountSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testowner', password='testpass123')
        
    def test_unauthorized_access(self):
        """Test Zugriffsbeschränkungen"""
        other_owner = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        guest = GuestAccount.objects.create(
            name='Security Test',
            username='security@example.com',
            owner=other_owner
        )
        
        # Versuche Zugriff auf fremden Guest
        response = self.client.get(
            reverse('guests:update', kwargs={'pk': guest.pk})
        )
        self.assertEqual(response.status_code, 403)
        
    def test_captcha_security(self):
        """Test Captcha-Sicherheit: fehlgeschlagene Verifizierung lehnt das Formular ab."""
        from unittest.mock import patch
        from django.core.exceptions import ValidationError
        from apps.guests.forms import GuestApplicationForm

        data = {
            'name': 'Test Guest',
            'username': 'newguest@example.com',
            'owner_email': self.owner.email,
            'message': 'Test message',
            'duration': 7,
        }
        with patch(
            'friendly_captcha.fields.FrcCaptchaField.clean',
            side_effect=ValidationError('captcha verification failed'),
        ):
            form = GuestApplicationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('captcha', form.errors)

class GuestAccountIntegrationTests(TestCase):

    def setUp(self):
        from django.contrib.auth.models import Permission
        
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testowner', password='testpass123')
        perm = Permission.objects.get(codename='sponsoring_access')
        self.owner.user_permissions.add(perm)
    
    @override_settings(FRC_CAPTCHA_MOCKED_VALUE=True)
    def test_complete_guest_lifecycle(self):

        """Test vollständiger Lebenszyklus eines Gast-Accounts"""
        # 1. Erstelle Antrag ueber das oeffentliche, anonyme Formular
        self.client.logout()
        response = self.client.post(reverse('guests:applicate'), {
            'name': 'Integration Test',
            'username': 'integration@example.com', 
            'owner_email': self.owner.email,
            'message': 'Integration test message',
            'duration': 7,
            'captcha': 'mocked_captcha_key',
        })

        # Prüfe ob Gast erstellt wurde
        guest = GuestAccount.objects.get(username='integration@example.com')
        self.assertIsNotNone(guest.created_at)
        # 2. Genehmige Antrag als eingeloggter Gastgeber
        self.client.login(username='testowner', password='testpass123')
        response = self.client.get(
            reverse('guests:approve', kwargs={'pk': guest.pk})
        )
        guest.refresh_from_db()
        self.assertTrue(guest.is_active)
        
        # 3. Verlängere Account
        response = self.client.post(
            reverse('guests:update', kwargs={'pk': guest.pk}),
            {'duration': 14, 'action': 'extend'}
        )
        guest.refresh_from_db()
        self.assertEqual(guest.extension_count, 1)
        
        # 4. Lösche Account
        response = self.client.post(
            reverse('guests:delete', kwargs={'pk': guest.pk})
        )
        guest.refresh_from_db()
        self.assertTrue(guest.is_deleted)
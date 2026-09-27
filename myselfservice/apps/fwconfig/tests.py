import uuid as uuid_lib

from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from apps.fwconfig.models import FirewallRule, FirewallRuleChange

class FwConfigTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Berechtigung hinzufügen
        permission = Permission.objects.get(codename='fwconfig_access')
        self.user.user_permissions.add(permission)
        
        # Firewall-Regel erstellen
        self.rule = FirewallRule.objects.create(
            uuid=uuid_lib.uuid4(),
            name='Internet G1R001',
            remote_rule_status=False,
        )

    def test_list_view_requires_permission(self):
        """Test dass die List View eine Berechtigung erfordert"""
        response = self.client.get(reverse('fwconfig:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_list_view_with_permission(self):
        """Test List View mit entsprechender Berechtigung"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('fwconfig:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rule.name)

    def test_toggle_rule(self):
        """Test das Umschalten einer Firewall-Regel (FakeFirewallService)"""
        self.client.login(username='testuser', password='testpass')
        
        # Regel einschalten
        response = self.client.post(reverse('fwconfig:toggle', args=[self.rule.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect nach toggle
        
        # Änderung sollte protokolliert worden sein
        change = FirewallRuleChange.objects.get(firewall_rule=self.rule)
        self.assertEqual(change.action, 'enabled')
        self.assertEqual(change.user, self.user)
        self.assertTrue(change.api_success)

    def test_firewall_rule_str(self):
        """Test String-Representation der FirewallRule"""
        rule = FirewallRule.objects.create(uuid=uuid_lib.uuid4(), name='Internet G1R101')
        self.assertEqual(str(rule), 'Internet G1R101')

    def test_firewall_rule_change_str(self):
        """Test String-Representation der FirewallRuleChange"""
        change = FirewallRuleChange.objects.create(
            firewall_rule=self.rule,
            user=self.user,
            action='enabled'
        )
        expected = f'{self.rule.name} - eingeschaltet - {self.user.username} ✗'
        self.assertEqual(str(change), expected)

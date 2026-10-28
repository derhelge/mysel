from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from ldap3 import MODIFY_ADD, MODIFY_REPLACE

from .services import LdapService


def ldap_config(mode):
    return {**settings.LDAP_MAIL_LOGIN_CONFIG, 'MODE': mode}


class LdapServiceModeTests(SimpleTestCase):
    def make_service(self):
        with patch('apps.emaildevice.services.Connection') as connection:
            conn = MagicMock()
            connection.return_value = conn
            service = LdapService()
        user = MagicMock(entry_dn='uid=testuser,ou=people,dc=example,dc=org')
        group = MagicMock(entry_dn='cn=B_MAIL_LOGIN_N,ou=groups,dc=example,dc=org')
        conn.entries = [user]
        conn.result = {'description': 'success'}
        return service, conn, user, group

    def test_group_mode_disables_login_via_group(self):
        service, conn, user, group = self.make_service()

        def search(*args, **kwargs):
            conn.entries = [user] if conn.search.call_count == 1 else [group]
        conn.search.side_effect = search

        with override_settings(LDAP_MAIL_LOGIN_CONFIG=ldap_config('group')):
            service.set_mail_login('testuser@example.org', False)

        conn.modify.assert_called_once_with(
            group.entry_dn, {'member': [(MODIFY_ADD, [user.entry_dn])]}
        )

    def test_attribute_mode_disables_login_via_attribute(self):
        service, conn, user, _ = self.make_service()

        with override_settings(LDAP_MAIL_LOGIN_CONFIG=ldap_config('attribute')):
            self.assertTrue(service.set_mail_login('testuser@example.org', False))

        conn.modify.assert_called_once_with(
            user.entry_dn, {'mailLoginByLdap': [(MODIFY_REPLACE, ['false'])]}
        )

    def test_attribute_mode_reads_attribute(self):
        service, conn, user, _ = self.make_service()
        user.mailLoginByLdap.value = True

        with override_settings(LDAP_MAIL_LOGIN_CONFIG=ldap_config('attribute')):
            self.assertTrue(service.get_mail_login('testuser@example.org'))

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount, SocialLogin

from apps.core.adapters import CustomSocialAccountAdapter

User = get_user_model()

class KeycloakPermissionMappingTest(TestCase):
    """Prüft das Rollen->Permission-Mapping im Adapter ohne echten Keycloak."""

    def setUp(self):
        self.factory = RequestFactory()
        self.adapter = CustomSocialAccountAdapter()

    def _sociallogin(self, roles):
        user = User(username='testuser1@example.org', email='testuser1@example.org')
        account = SocialAccount(
            provider='keycloak',
            uid='keycloak-1',
            extra_data={
                'userinfo': {
                    'email': 'testuser1@example.org',
                    'given_name': 'Test',
                    'family_name': 'User',
                    'resource_access': {'django': {'roles': roles}},
                }
            },
        )
        return SocialLogin(user=user, account=account)

    def test_mapped_role_grants_permission(self):
        sociallogin = self._sociallogin(['B_MYSEL_EDUROAM_ACCESS'])
        self.adapter.pre_social_login(self.factory.get('/'), sociallogin)

        self.assertTrue(
            sociallogin.user.user_permissions.filter(codename='eduroam_access').exists()
        )

    def test_unmapped_role_grants_no_permission(self):
        sociallogin = self._sociallogin(['SOME_UNKNOWN_ROLE'])
        self.adapter.pre_social_login(self.factory.get('/'), sociallogin)

        self.assertEqual(sociallogin.user.user_permissions.count(), 0)
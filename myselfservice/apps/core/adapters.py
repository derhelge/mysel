from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Permission, User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def link_pending_guest_accounts(user):
    """
    Verknüpft pending Gast-Accounts mit dem User, wenn temp_owner_email übereinstimmt
    """
    try:
        from apps.guests.models import GuestAccount
        pending_guests = GuestAccount.objects.filter(
            temp_owner_email=user.email,
            owner__isnull=True,
            status=GuestAccount.Status.PENDING
        )
        
        count = pending_guests.count()
        if count > 0:
            pending_guests.update(owner=user, temp_owner_email=None)
            logger.info(f"Linked {count} pending guest account(s) to user {user.email}")
    except Exception as e:
        logger.error(f"Error linking pending guest accounts for {user.email}: {str(e)}", exc_info=True)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        logger.debug(f"Populated user ({user}) with data: {data}")
        return user
            
    def _get_roles_from_provider(self, extra_data, provider_id):
        """
        Extrahiert Rollen basierend auf dem Provider
        """
        if provider_id == "keycloak":
            userinfo = extra_data.get('userinfo', {})
            resource_access = userinfo.get('resource_access', {})
            client_access = resource_access.get('django', {})
            return client_access.get('roles', [])
        elif provider_id == "shibboleth":
            userinfo = extra_data.get('userinfo', {})
            return userinfo.get('roles', [])
        return []

    def _get_user_info(self, extra_data, provider_id):
        """
        Extrahiert Benutzerinformationen basierend auf dem Provider
        """
        if provider_id in ["keycloak", "shibboleth"]:
            userinfo = extra_data.get('userinfo', {})
            email = userinfo.get('email', '')
            return {
                'first_name': userinfo.get('given_name', ''),
                'last_name': userinfo.get('family_name', ''),
                'email': email.lower() if email else '',
            }
        return {}

    def pre_social_login(self, request, sociallogin):
        try:
            extra_data = sociallogin.account.extra_data
            provider_id = sociallogin.account.provider
            username = sociallogin.user.username.lower()

            logger.debug(f"Processing login for provider: {provider_id}")
            logger.debug(f"Extra data from social login: {extra_data}")

            if username:
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    # Benutzerinformationen basierend auf Provider abrufen
                    user_info = self._get_user_info(extra_data, provider_id)
                    
                    # Aktualisiere User-Daten
                    for key, value in user_info.items():
                        setattr(existing_user, key, value)
                    existing_user.save()
                    
                    logger.debug(f"Updated existing user data for {existing_user.username}")
                    
                    # Verbinde Social Account mit existierendem User
                    sociallogin.user = existing_user
                    sociallogin.connect(request, existing_user)

            # Rollen basierend auf Provider abrufen
            client_roles = self._get_roles_from_provider(extra_data, provider_id)
            logger.debug(f"Found client roles: {client_roles}")

            # User erst speichern
            sociallogin.user.save()

            # Berechtigungen zuweisen
            role_map_upper = {k.upper(): v for k, v in settings.PERMISSION_MAPPING.items()}
            logger.debug(f"Permission mapping: {role_map_upper}")
            
            for role_name in client_roles:
                if role_name.upper() in role_map_upper:
                    logger.debug(f"Mapping role '{role_name}' to permission '{role_map_upper[role_name.upper()]}'")
                    app_label, codename = role_map_upper[role_name.upper()].split('.')
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label
                        )
                        sociallogin.user.user_permissions.add(permission)
                        logger.debug(f"Added permission '{role_map_upper[role_name.upper()]}' to user {sociallogin.user}")
                    except Permission.DoesNotExist:
                        logger.warning(f"Permission {role_map_upper[role_name.upper()]} does not exist")

            # Verknüpfe pending Gast-Accounts beim Login
            link_pending_guest_accounts(sociallogin.user)

        except Exception as e:
            logger.error(f"Error in pre_social_login: {str(e)}", exc_info=True)
                
        return super().pre_social_login(request, sociallogin)
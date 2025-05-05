from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Permission, User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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
            resource_access = extra_data.get('resource_access', {})
            client_access = resource_access.get('django', {})
            return client_access.get('roles', [])
        elif provider_id == "shibboleth":
            return extra_data.get('roles', [])
        return []

    def _get_user_info(self, extra_data, provider_id):
        """
        Extrahiert Benutzerinformationen basierend auf dem Provider
        """
        if provider_id == "keycloak":
            return {
                'first_name': extra_data.get('given_name', ''),
                'last_name': extra_data.get('family_name', ''),
                'email': extra_data.get('email', ''),
            }
        elif provider_id == "shibboleth":
            name_parts = extra_data.get('name', '').split()
            return {
                'first_name': name_parts[0] if name_parts else '',
                'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                'email': extra_data.get('email', ''),
            }
        return {}

    def pre_social_login(self, request, sociallogin):
        try:
            extra_data = sociallogin.account.extra_data
            provider_id = sociallogin.account.provider
            username = sociallogin.user.username
            
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

            for role_name in client_roles:
                if role_name.upper() in role_map_upper:
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

        except Exception as e:
            logger.error(f"Error in pre_social_login: {str(e)}", exc_info=True)
                
        return super().pre_social_login(request, sociallogin)
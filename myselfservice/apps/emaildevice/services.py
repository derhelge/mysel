from django.conf import settings
from ldap3 import Server, Connection, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE
import logging

logger = logging.getLogger(__name__)

class LdapService:
    def __init__(self):
        self.server = Server(settings.LDAP_MAIL_LOGIN_CONFIG['SERVER_URI'])
        self.conn = Connection(
            self.server,
            settings.LDAP_MAIL_LOGIN_CONFIG['BIND_DN'],
            settings.LDAP_MAIL_LOGIN_CONFIG['BIND_PASSWORD'],
            auto_bind=True
        )

    def set_mail_login(self, username, value):
        """
        Set mail login status by adding/removing user from B_MAIL_LOGIN_N group.
        value=True: Enable mail login (remove from group)
        value=False: Disable mail login (add to group)
        """
        if settings.LDAP_MAIL_LOGIN_CONFIG['MODE'] == 'attribute':
            return self._set_mail_login_attribute(username, value)

        # Find user DN
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['USER_BASE_DN'],
                        f'(userPrincipalName={username})',
                        attributes=['distinguishedName'])
        
        if not self.conn.entries:
            logger.error(f"User {username} not found in LDAP")
            return False
        
        user_dn = self.conn.entries[0].entry_dn
        
        # Find group DN
        group_name = settings.LDAP_MAIL_LOGIN_CONFIG['MAIL_LOGIN_DISABLED_GROUP']
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['GROUP_BASE_DN'],
                        f'(cn={group_name})',
                        attributes=['distinguishedName'])
        
        if not self.conn.entries:
            logger.error(f"Group {group_name} not found in LDAP")
            return False
        
        group_dn = self.conn.entries[0].entry_dn
        
        # Add or remove user from group based on value
        if value:  # Enable mail login = remove from group
            operation = MODIFY_DELETE
            action = "removed from"
        else:  # Disable mail login = add to group
            operation = MODIFY_ADD
            action = "added to"
        
        success = self.conn.modify(group_dn, {'member': [(operation, [user_dn])]})
        
        if success:
            logger.info(f"User {username} successfully {action} group {group_name}")
        else:
            logger.error(f"Failed to modify group membership for {username}: {self.conn.result}")
        
        return success
    
    def get_mail_login(self, username):
        """
        Check if mail login is enabled by checking if user is NOT in B_MAIL_LOGIN_N group.
        Uses efficient LDAP query instead of loading all group members.
        Returns True if mail login is enabled, False if disabled.
        """
        if settings.LDAP_MAIL_LOGIN_CONFIG['MODE'] == 'attribute':
            return self._get_mail_login_attribute(username)

        # Find user DN
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['USER_BASE_DN'],
                        f'(userPrincipalName={username})',
                        attributes=['distinguishedName'])

        if not self.conn.entries:
            logger.error(f"User {username} not found in LDAP")
            return False
        
        user_dn = self.conn.entries[0].entry_dn
        group_name = settings.LDAP_MAIL_LOGIN_CONFIG['MAIL_LOGIN_DISABLED_GROUP']
        
        # Search for the group with the user as member
        # This avoids loading all group members locally
        self.conn.search(
            settings.LDAP_MAIL_LOGIN_CONFIG['GROUP_BASE_DN'],
            f'(&(cn={group_name})(member={user_dn}))',
            attributes=['cn']
        )
        
        # If the search returns results, the user is in the disabled group
        is_in_disabled_group = len(self.conn.entries) > 0
        
        # If user is NOT in the group, mail login is enabled
        return not is_in_disabled_group

    def _set_mail_login_attribute(self, username, value):
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['USER_BASE_DN'],
                        f'(userPrincipalName={username})',
                        attributes=['distinguishedName'])

        if not self.conn.entries:
            return False
        user_dn = self.conn.entries[0].entry_dn
        self.conn.modify(user_dn,
            {'mailLoginByLdap': [(MODIFY_REPLACE, [str(value).lower()])]})
        return self.conn.result['description'] == 'success'

    def _get_mail_login_attribute(self, username):
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['USER_BASE_DN'],
                        f'(userPrincipalName={username})',
                        attributes=['mailLoginByLdap'])

        if not self.conn.entries:
            return False
        return bool(self.conn.entries[0].mailLoginByLdap.value)
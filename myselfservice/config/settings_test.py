# config/settings_test.py
"""Settings für lokale Unit-Tests ohne Docker-Stack (SQLite, keine externen Dienste)."""
import os

# Pflicht-Env-Vars vorbelegen, bevor settings.py sie über django-environ einliest.
_DEFAULTS = {
    'SECRET_KEY': 'test-secret-key-not-for-production',
    'DEBUG': 'False',
    'DJANGO_OIDC_SECRET': 'test',
    'SSO_PROVIDER': 'keycloak',
    'SHIBBOLETH_CLIENT_ID': 'test',
    'SHIBBOLETH_OIDC_SECRET': 'test',
    'SHIBBOLETH_SERVER_URL': 'https://example.org/.well-known/openid-configuration',
    'FRC_CAPTCHA_SECRET': 'test',
    'FRC_CAPTCHA_SITE_KEY': 'test',
    'FRC_CAPTCHA_MOCKED_VALUE': 'False',
    'POSTGRES_REPLICATION_USER': 'replication',
    'POSTGRES_DJANGO_DB': 'django',
    'POSTGRES_DJANGO_USER': 'django',
    'POSTGRES_DJANGO_PASSWORD': 'django',
    'LDAP_MAIL_SERVER_URI': 'ldap://localhost:389',
    'LDAP_MAIL_BIND_DN': 'cn=admin,dc=example,dc=org',
    'LDAP_MAIL_BIND_PASSWORD': 'test',
    'LDAP_MAIL_USER_BASE_DN': 'ou=users,dc=example,dc=org',
    'WLAN_LOGIN_URL': 'https://example.org/wlan-login',
    'USE_FAKE_FIREWALL': 'True',
}
for _key, _value in _DEFAULTS.items():
    os.environ.setdefault(_key, _value)

from .settings import *  # noqa: E402,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Keine externen Dienste im lokalen Testlauf: nur Django-User als E-Mail-Quelle.
LOOKUP_DJANGO_USERS = True
LOOKUP_LDAP_SERVERS = []
if 'LOOKUP_EMAIL_FILE_CONFIG' in globals():
    del LOOKUP_EMAIL_FILE_CONFIG  # noqa: F821

USE_FAKE_FIREWALL = True

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
LOGGING['loggers']['']['level'] = 'WARNING'  # noqa: F405

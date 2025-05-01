# config/settings.py
import environ
import sys

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Environment variables
env = environ.Env(DEBUG=(bool, False))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
OIDC_SECRET = env('DJANGO_OIDC_SECRET')
SHIBBOLETH_CLIENT_ID = env('SHIBBOLETH_CLIENT_ID')
SHIBBOLETH_OIDC_SECRET = env('SHIBBOLETH_OIDC_SECRET')
SHIBBOLETH_SERVER_URL = env('SHIBBOLETH_SERVER_URL')

FRC_CAPTCHA_SECRET = env('FRC_CAPTCHA_SECRET')
FRC_CAPTCHA_SITE_KEY = env('FRC_CAPTCHA_SITE_KEY')

ALLOWED_HOSTS = ['localhost','127.0.0.1','myselfservice']
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1','http://myselfservice']

BASE_URL = env('BASE_URL', default='http://myselfservice:8000')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    'django.contrib.sites',
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid_connect',
    "crispy_forms",
    "crispy_bootstrap4",
    "friendly_captcha",
]

INSTALLED_APPS += [
    'apps.core.apps.CoreConfig',
    'apps.guests.apps.GuestsConfig',
    'apps.eduroam.apps.EduroamConfig',
    'apps.events.apps.EventsConfig',
    'apps.emaildevice.apps.EmailDeviceConfig',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DJANGO_DB'),
        'USER': env('POSTGRES_DJANGO_USER'),
        'PASSWORD': env('POSTGRES_DJANGO_PASSWORD'),
        'HOST': 'postgres',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_django',
        },
    }    
}

AUTHENTICATION_BACKENDS = [
    #'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
#ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET=True
SOCIALACCOUNT_LOGOUT_ON_GET = True

SSO_PROVIDER = env.str('SSO_PROVIDER', default='keycloak')
OIDC_BASE_CONFIG = {
    'VERIFIED_EMAIL': False,
}

PROVIDER_CONFIGS = {
    'keycloak':{
        "provider_id": "keycloak",
        "name": "SSO",
        "client_id": "django",
        "secret": OIDC_SECRET,
        "settings": {
            "server_url": "http://keycloak:8080/realms/example/.well-known/openid-configuration",
            "scope": ['openid', 'profile', 'email', 'roles'],
        },
    },
    'shibboleth': {
        "provider_id": "shibboleth",
        "name": "SSO",
        "client_id": SHIBBOLETH_CLIENT_ID,
        "secret": SHIBBOLETH_OIDC_SECRET,
        "settings": {
            "server_url": SHIBBOLETH_SERVER_URL,
            "scope": ['openid', 'profile', 'email', 'roles'],
        },
    }
}

SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        **OIDC_BASE_CONFIG,
        "APPS": [PROVIDER_CONFIGS[SSO_PROVIDER]]
    }
}

CUSTOM_LOGOUT_OIDC = "http://keycloak:8080/realms/example/protocol/openid-connect/logout"

SOCIALACCOUNT_ADAPTER = 'apps.core.adapters.CustomSocialAccountAdapter'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / 'static']

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Für Entwicklung
DEFAULT_FROM_EMAIL = 'noreply@example.com'


LOGIN_URL = '/accounts/oidc/keycloak/login/'
LOGIN_REDIRECT_URL = 'core:home' 
ACCOUNT_LOGOUT_REDIRECT_URL = 'core:home'

# AllAuth Settings

SITE_ID = 1

#############################
# Guest settings
############################
WLAN_LOGIN_URL = 'https://wifi.example.com'  # Anpassen an tatsächliche URL

##############
# LDAP Lookup (Falls Gastgeber noch keinen Account hat)
##############
LOOKUP_LDAP_SERVERS = [
    {
        'uri': env('LDAP_MAIL_SERVER_URI'),
        'bind_dn': env('LDAP_MAIL_BIND_DN'),
        'bind_pw': env('LDAP_MAIL_BIND_PASSWORD'),
        'base_dn': 'dc=example,dc=org',
        'filter': '(mail={email})',
        'mail_attr': 'mail'
    },
#     {
#         'uri': 'ldap://server2:389',
#         'bind_dn': 'cn=reader,ou=users,dc=example2,dc=com', 
#         'bind_pw': 'secret2',
#         'base_dn': 'ou=users,dc=example2,dc=com',
#         'filter': '(userPrincipalName={email})',
#         'mail_attr': 'userPrincipalName'
#     }
]
LOOKUP_EMAIL_FILE_CONFIG = {
    'file_path': BASE_DIR / "lookup_email.txt"
}
LOOKUP_DJANGO_USERS = True


GUEST_SETTINGS = {
    'LIMIT_ACTIVE_GUESTS': 5,  # Maximum number of active guests per owner
    'LIMIT_EXTEND_GUEST': 3,    # Maximum number of extensions per guest
}

PERMISSION_REQUIRED = {
    'GUEST_MANAGEMENT': 'guests.sponsoring_access',
    'EDUROAM_ACCESS': 'eduroam.eduroam_access',
    'EVENTS_MANAGEMENT': 'events.events_access',
    'EMAILDEVICE_ACCESS': 'emaildevice.emaildevice_access',
}

#############################
# App settings
############################
EDUROAM_SETTINGS = {
    'MAX_ACCOUNTS': 5,  # Maximum number of active accounts per user
    'REALM': 'thga.de',  # Default realm
}

EVENT_SETTINGS = {
    'MAX_ACCOUNTS' : 200,
}

EMAILDEVICE_SETTINGS = {
    'MAX_ACCOUNTS': 5,  # Maximum number of active accounts per user
    'REALM': 'stud.thga.de',  # Default realm
    'PASSWORD_LENGTH': 12,
    'DEACTIVATE_LDAP_LOGIN_AFTER_CREATE': True
}
LDAP_MAIL_LOGIN_CONFIG = {
    'SERVER_URI': env('LDAP_MAIL_SERVER_URI'),
    'BIND_DN': env('LDAP_MAIL_BIND_DN'),
    'BIND_PASSWORD': env('LDAP_MAIL_BIND_PASSWORD'),
    'USER_BASE_DN': env('LDAP_MAIL_USER_BASE_DN'),
}

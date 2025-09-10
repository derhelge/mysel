# apps/core/utils.py
import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_admin_notification(obj, action):
    """Benachrichtigt alle Superuser per E-Mail"""
    User = get_user_model()
    superuser_emails = User.objects.filter(
        is_superuser=True, 
        email__isnull=False
    ).exclude(email='').values_list('email', flat=True)
    
    if not superuser_emails:
        return
    
    model_name = obj._meta.verbose_name
    subject = f"[Django] {model_name} {action}"
    message = f"{model_name} wurde {action}:\n\n{obj}"
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=list(superuser_emails),
        fail_silently=True
    )

def generate_password(length=7):
    """Generiert ein sicheres Passwort ohne verwechselbare Zeichen."""
    alphabet = string.ascii_letters + string.digits
    # Entferne verwechselbare Zeichen
    alphabet = ''.join(c for c in alphabet if c not in 'lLIO0o')
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    
    if length > 7:
        chunks = [password[i:i+4] for i in range(0, len(password), 4)]
        return '-'.join(chunks)
    return password

def send_mail_template(subject, template_name, context, recipient_list):
    """
    Zentrale Funktion zum Versenden von Template-basierten Emails.
    
    Args:
        subject (str): Betreff der Email
        template_name (str): Pfad zum HTML-Template
        context (dict): Kontext-Variablen für das Template
        recipient_list (list): Liste der Empfänger-Emailadressen
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    return send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=True,
    )

from abc import ABC, abstractmethod
from django.conf import settings
from django.contrib.auth import get_user_model

from ldap3 import Server, Connection, SAFE_SYNC, SUBTREE, ALL
import msal
import csv

class EmailValidator(ABC):
    @abstractmethod 
    def validate_email(self, email):
        """Validate if email exists in source"""
        pass

class LDAPValidator(EmailValidator):
    def __init__(self, config):
        self.config = config
        
    def validate_email(self, email):
        logger.debug(f"Validating email {email} against LDAP {self.config['uri']}")
        server = Server(
            self.config['uri'],
            connect_timeout=0.25,
            use_ssl=True
        )
        conn = Connection(
            server,
            self.config['bind_dn'],
            self.config['bind_pw'],
        )

        if not conn.bind():
            logger.error(f"LDAP bind failed to {self.config['uri']}.")
            return False
        
        conn.search(
            search_base=self.config['base_dn'],
            search_scope=SUBTREE,
            search_filter=self.config['filter'].format(email=email),
            attributes=[self.config['mail_attr']]
        )
        logger.debug(f"LDAP search completed with {len(conn.entries)} entries.")
        return bool(conn.entries)

class AzureADValidator(EmailValidator):
    def __init__(self, config):
        self.config = config
        self.msal_app = msal.ConfidentialClientApplication(
            self.config['client_id'],
            authority=f"https://login.microsoftonline.com/{self.config['tenant_id']}",
            client_credential=self.config['client_secret'],
        )

    def validate_email(self, email):
        result = self.msal_app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" in result:
            # Hier Graph API call für User-Prüfung
            # Vereinfacht dargestellt
            return True
        return False

class TextFileValidator(EmailValidator):
    def __init__(self, config):
        self.config = config
        
    def validate_email(self, email):
        with open(self.config['file_path'], 'r') as f:
            reader = csv.reader(f)
            return any(email.lower() == row[0].lower() for row in reader)

class DjangoUserValidator(EmailValidator):
    def validate_email(self, email):
        User = get_user_model()
        return User.objects.filter(email=email.lower()).exists()

class MultiSourceValidator:
    def get_validators(self):
        validators = []
        
        # LDAP Validator(s)
        if hasattr(settings, 'LOOKUP_LDAP_SERVERS'):
            for config in settings.LOOKUP_LDAP_SERVERS:
                validators.append(LDAPValidator(config))
            
        # Azure AD
        if hasattr(settings, 'LOOKUP_AZURE_AD_CONFIG'):
            validators.append(AzureADValidator(settings.LOOKUP_AZURE_AD_CONFIG))
            
        # Text file
        if hasattr(settings, 'LOOKUP_EMAIL_FILE_CONFIG'):
            validators.append(TextFileValidator(settings.LOOKUP_EMAIL_FILE_CONFIG))

        # Django User DB
        if getattr(settings, 'LOOKUP_DJANGO_USERS', True):
            validators.append(DjangoUserValidator())

        return validators

    def validate_email(self, email):
        for validator in self.get_validators():
            try:
                if isinstance(validator, DjangoUserValidator):
                    if validator.validate_email(email):
                        logger.info(f"Email {email} found in Source: Django users")
                        return True
                elif isinstance(validator, LDAPValidator):
                    if validator.validate_email(email):
                        logger.info(f"Email {email} found in Source: LDAP {validator.config['uri']}")
                        return True
                elif isinstance(validator, TextFileValidator): 
                    if validator.validate_email(email):
                        logger.info(f"Email {email} found in Source: File {validator.config['file_path']}")
                        return True
                elif isinstance(validator, AzureADValidator):
                    if validator.validate_email(email):
                        logger.info(f"Email {email} found in Source: Azure AD")
                        return True
            except Exception:
                continue
        return False
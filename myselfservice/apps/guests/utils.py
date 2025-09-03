# apps/guests/utils.py
from django.conf import settings

from apps.core.utils import send_mail_template

# apps/guests/utils.py
def send_guest_notification(guest, action):
    """Benachrichtigt den Gast über seinen Account-Status"""
    context = {
        'guest': guest,
        'credentials': {
            'username': guest.username,
            'password': guest.password
        }
    }
    
    if action == 'applicate':
        template = 'guests/emails/application_received.html'  # Pfad korrigiert
        subject = 'Ihr WLAN-Zugang wurde beantragt'
    else:
        template = 'guests/emails/account_activated.html'  # Pfad korrigiert
        if action == 'activate' or action == 'approve':
            subject = 'Ihr WLAN-Zugang wurde aktiviert'
        elif action == 'extend':
            subject = 'Ihr WLAN-Zugang wurde verlängert'
        elif action == 'reactivate':
            subject = 'Ihr WLAN-Zugang wurde reaktiviert'

    send_mail_template(
        subject=subject,
        template_name=template,
        context=context,
        recipient_list=[guest.username]
    )
    
def send_owner_notification(guest, temp_owner_email = None):
    """Benachrichtigt den Owner über einen neuen Antrag."""
    if not guest.is_pending:
        return
    
    if temp_owner_email is None:
        email = guest.owner.email
    else:
        email = temp_owner_email
    
    context = {
        'guest': guest,
        'approval_url': f"{settings.BASE_URL}/guests/{guest.id}/approve/"
    }
    
    send_mail_template(
        subject='Neuer Gast-WLAN Antrag',
        template_name='guests/emails/owner_notification.html',
        context=context,
        recipient_list=[email]
    )



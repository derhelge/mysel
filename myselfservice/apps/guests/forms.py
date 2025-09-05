from django import forms

from .models import GuestAccount
from friendly_captcha.fields import FrcCaptchaField
from apps.core.utils import MultiSourceValidator

class GuestForm(forms.ModelForm):

    class Meta:
        model = GuestAccount
        fields = ['name', 'username', 'message', 'duration']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 1})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "E-Mail Adresse des Gastes (wird zu Username)"

    def clean_username(self):
        return self.cleaned_data['username'].lower()

class GuestApplicationForm(GuestForm):
    owner_email = forms.EmailField(label="E-Mail-Adresse Ihres Gastgebers")
    captcha = FrcCaptchaField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Ihr Name"
        self.fields['username'].label = "Ihre E-Mail Adresse"
        self.fields['message'].label = "Mitteilung an den Gastgeber"
 
    def clean_owner_email(self):
        email = self.cleaned_data['owner_email'].lower()
        backend = MultiSourceValidator()
        if not backend.validate_email(email=email):
            raise forms.ValidationError("E-Mail Adresse wurde nicht gefunden")
        return email
    
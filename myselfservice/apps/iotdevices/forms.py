# forms.py
from django import forms
from .models import IotDeviceAccount

class IotDeviceAccountForm(forms.ModelForm):
    class Meta:
        model = IotDeviceAccount
        fields = ['device_name', 'mac_address']
        widgets = {
            'device_name': forms.TextInput(attrs={'placeholder': 'z.B. Wetterstation WBx G1R666'}),
            'mac_address': forms.TextInput(attrs={'placeholder': 'AA:BB:CC:DD:EE:FF'})
        }

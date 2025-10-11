from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'contact', 'start_date', 'end_date', 
                 'number', 'nameprefix', 'comment']
        
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 3}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nameprefix'].help_text = "Die generierten Usernamen werden aus diesem Prefix und einer Nummer bestehen"
        self.fields['contact'].help_text ="Geben Sie die Email-Adresse für einen Ansprechpartner für diese Veranstaltung an"
        # Bei Updates (wenn instance vorhanden ist) das number-Feld readonly machen
        if self.instance and self.instance.pk:
            self.fields['number'].widget.attrs['readonly'] = True
            self.fields['nameprefix'].widget.attrs['readonly'] = True
            self.fields['number'].help_text = "Die Useranzahl kann bei bestehenden Events nicht mehr geändert werden"
            self.fields['nameprefix'].help_text = "Die Usernamen können bei bestehenden Events nicht mehr geändert werden"

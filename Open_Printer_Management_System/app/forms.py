from django import forms

from .models import Printer

class AddPrinterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['printer_name'].widget.attrs.update(size='34')
        self.fields['printer_location'].widget.attrs.update(size='34')
        self.fields['ip_address'].widget.attrs.update(size='34')
        self.fields['department_name'].widget.attrs.update(size='34')
    
    class Meta:
        model = Printer
        fields = ['printer_name', 'printer_location', 'ip_address', 'department_name']

class SiteToggles(forms.Form):
    ip_address = forms.BooleanField(required=False, initial=True, label="Show IP Address",
        widget=forms.CheckboxInput(
            attrs={
                'class': 'custom-control-input',
                'id': 'ip_address',
                'onChange': 'submit()'
            }
        )
    )

    location = forms.BooleanField(required=False, initial=True, label="Show Location",
        widget=forms.CheckboxInput(
            attrs={
                'class': 'custom-control-input',
                'id': 'location',
                'onChange': 'submit()'
            }
        )
    )

    printer_model = forms.BooleanField(required=False, initial=False, label="Show Model",
        widget=forms.CheckboxInput(
            attrs={
                'class': 'custom-control-input',
                'id': 'printer_model',
                'onChange': 'submit()'
            }
        )
    )
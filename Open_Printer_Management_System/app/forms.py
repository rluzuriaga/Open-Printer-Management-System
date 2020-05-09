from django import forms

from .models import Printer

class AddPrinterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['printer_name'].widget.attrs.update(size='34')
        self.fields['printer_model_name'].widget.attrs.update(size='34')
        self.fields['printer_location'].widget.attrs.update(size='34')
        self.fields['ip_address'].widget.attrs.update(size='34')
        self.fields['department_name'].widget.attrs.update(size='34')
    
    class Meta:
        model = Printer
        fields = ['printer_name', 'printer_model_name', 'printer_location', 'ip_address', 'department_name']
from django import forms

from .models import Printer

class AddPrinterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['printer_name']
        self.fields['printer_model_name']
        self.fields['printer_location']
        self.fields['ip_address']
        self.fields['department_name']
    
    class Meta:
        model = Printer
        fields = ['printer_name', 'printer_model_name', 'printer_location', 'ip_address', 'department_name']
from django.db import models
from django.conf import settings
from django.utils import timezone

class Printer(models.Model):
    printer_name = models.CharField(
        'Printer Name',
        max_length=75,
        help_text="Name of printer on server. Example: IT Copier OR 8x11_1125."
    )
    printer_model_name = models.CharField(
        'Printer Model Name',
        max_length=75,
        help_text="Printer model name. Example: HP LaserJet m402dn."
    )
    printer_location = models.CharField(
        'Printer Location',
        max_length=50,
        help_text="Location of printer. Example: Building 8 Room 45 OR 8-45"
    )
    ip_address = models.CharField(
        'IP Address',
        max_length=15,
        unique=True,
        help_text="IPv4 address of the printer."
    )
    department_name = models.CharField(
        'Department Name',
        max_length=50,
        help_text="What department is this printer in?"
    )
    snmp_version = models.IntegerField('SNMP Version', default=1)

    def __str__(self):
        return self.printer_name

class TonerLevel(models.Model):
    printer_name = models.ForeignKey(Printer, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    module_identifier = models.CharField(
        max_length=50,
        help_text="Identifier for the toners or units. Example. Magenta OR Toner Collection Unit."
    )
    level = models.CharField(max_length=3, help_text="This should be either a percentage (0 - 100 without the percent sign) or OK or NA.")

    def __str__(self):
        return str(self.printer_name)

def update_database(printer_levels_dict):
    ''' Update the TonerLevel Table in the database with the information in the dictionary argument.

    Args:
        printer_levels_dict (dict): Dictionary with toner levels data.
            DICTIONARY STRUCTURE:
                {
                    'PRINTER NAME': {
                        'MODULE IDENTIFIER/TONER COLOR': 'LEVEL',
                        'Cyan': '13', ...
                    },
                    '8X11_2232': {...}
                    ...
                }
    '''

    for key_top, value_dict in printer_levels_dict.items():
        for key, value in value_dict.items():
            TonerLevel.objects.create(
                printer_name=Printer.objects.get(printer_name=key_top),
                module_identifier=key,
                level=value
            )

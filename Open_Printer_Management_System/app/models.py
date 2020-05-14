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
        help_text="IPv4 address of the printer."
    )
    department_name = models.CharField(
        'Department Name',
        max_length=50,
        help_text="What department is this printer in?"
    )

    def __str__(self):
        return self.printer_name

class TonerLevel(models.Model):
    printer_name = models.ForeignKey(Printer, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    module_identifier = models.CharField(
        max_length=20,
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
                        'Cyan Cartridge 508A HP CF361A': '13', ...
                    },
                    '8X11_2232': {...}
                    ...
                }
    '''
    # Check for redundancy. If the database already has the same toner levels just update the datetime field.
    time_threshold = timezone.now() - settings.TIMEDELTA
    query = TonerLevel.objects.filter(date_time__gt=time_threshold)

    for key_top, value_dict in printer_levels_dict.items():
        for key, value in value_dict.items():
            # If the value of the toner data already in the database (up to an hour before) is the same as the printer_levels_dict
            #   then the database doesn't get updated
            try:
                query_check = query.get(
                    printer_name=Printer.objects.get(printer_name=key_top),
                    module_identifier=key).level
            except TonerLevel.DoesNotExist:
                query_check = {}

            if len(query_check) != 0 and query_check == value:
                continue

            TonerLevel.objects.create(
                printer_name=Printer.objects.get(printer_name=key_top),
                module_identifier=key,
                level=value
            )

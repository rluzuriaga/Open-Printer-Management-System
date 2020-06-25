from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from app.snmp import SNMP
from app.models import Printer, update_database, TonerLevel
from app.views import toner_level_cleanup

import random

class Command(BaseCommand):
    help = 'Updates the database with the newest toner data.'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--ip', dest='ip')
        parser.add_argument('-n', '--name', dest='name')
        parser.add_argument('-m', '--module-number', dest='module_number')

    """
    def handle(self, *args, **options):
        ip = options['ip']
        name = options['name']

        printer_levels_dict = dict()

        if ip and name:
            version = Printer.objects.get(ip_address=ip).snmp_version

            levels_dict = SNMP(ip, version).get_consumable_levels()
            printer_levels_dict[name] = levels_dict
            update_database(printer_levels_dict)
            return

        all_printers_object = Printer.objects.all()

        printer_dict = {printer.printer_name: printer.ip_address for printer in all_printers_object}

        for printer_name, ip_address in printer_dict.items():
            version = Printer.objects.get(ip_address=ip_address).snmp_version

            levels_dict = SNMP(ip_address, version).get_consumable_levels()
            printer_levels_dict[printer_name] = levels_dict
        
        update_database(printer_levels_dict)
    """

    def handle(self, *args, **options):
        ip = options['ip']
        name = options['name']
        module_number = options['module_number']

        printer_levels_dict = dict()

        # Only runs when a new printer is added.
        # Create random percentage (from 30 to 100) for the printer.
        if ip is not None and name is not None and module_number is not None:
            rand1 = str(random.randint(30, 100))
            rand2 = str(random.randint(30, 100))
            rand3 = str(random.randint(30, 100))
            rand4 = str(random.randint(30, 100))
            rand5 = str(random.randint(30, 100))
            rand6 = str(random.randint(30, 100))

            if module_number == '1':
                printer_levels_dict[name] = {'Black': rand1}
            elif module_number == '3':
                printer_levels_dict[name] = {
                    'Black': rand1,
                    'Clean Rollers HP': rand2,
                    'Document Feeder Kit HP L2718A': rand3
                }
            elif module_number == '4':
                printer_levels_dict[name] = {
                    'Black': rand1,
                    'Cyan': rand2,
                    'Magenta': rand3,
                    'Yellow': rand4
                }
            elif module_number == '6':
                printer_levels_dict[name] = {
                    'Cyan': rand1,
                    'Gray': rand2,
                    'Magenta': rand3,
                    'Matte Black': rand4,
                    'Photo Black': rand5,
                    'Yellow': rand6
                }
            
            update_database(printer_levels_dict)
            return

        # Runs everytime that the toner data gets refreshed either manually or using cron.
        else:
            time_threshold = timezone.now() - settings.TIMEDELTA_PLUS_ONE
            all_toner_levels = TonerLevel.objects.filter(date_time__gte=time_threshold).distinct().order_by('printer_name', 'module_identifier')

            for toner in all_toner_levels:
                printer_name = str(toner.printer_name)
                module_id = str(toner.module_identifier)

                level = int(toner.level)
                if level == 0:
                    new_level = random.randint(95, 100)
                else:
                    rand = random.randint(1, 3)
                    new_level = level - rand
                    if new_level < 0:
                        new_level = 0
                
                new_level = str(new_level)

                try:
                    printer_levels_dict[printer_name].update({module_id: new_level})
                except KeyError:
                    printer_levels_dict[printer_name] = {module_id: new_level}
            
            TonerLevel.objects.filter(date_time__gte=time_threshold).distinct().order_by('printer_name', 'module_identifier').delete()

            update_database(printer_levels_dict)
            return

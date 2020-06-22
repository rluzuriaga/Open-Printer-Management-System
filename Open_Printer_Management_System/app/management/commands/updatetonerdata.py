from django.core.management.base import BaseCommand, CommandError

from app.snmp import SNMP
from app.models import Printer, update_database

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
        
        print(options)

        printer_levels_dict = dict()

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

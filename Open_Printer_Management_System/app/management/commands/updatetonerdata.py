from django.core.management.base import BaseCommand, CommandError

from app.snmp import SNMP
from app.models import Printer, update_database

class Command(BaseCommand):
    help = 'Updates the database with the newest toner data.'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--ip', dest='ip')
        parser.add_argument('-n', '--name', dest='name')

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

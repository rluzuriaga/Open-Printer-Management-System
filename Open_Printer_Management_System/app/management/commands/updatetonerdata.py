from django.core.management.base import BaseCommand, CommandError

from app.snmp import SNMP
from app.models import Printer, update_database

class Command(BaseCommand):
    help = 'Updates the database with the newest toner data.'

    def handle(self, *args, **options):
        all_printers_object = Printer.objects.all()

        printer_dict = {printer.printer_name: printer.ip_address for printer in all_printers_object}

        printer_levels_dict = dict()

        for printer_name, ip_address in printer_dict.items():
            levels_dict = SNMP(ip_address).get_consumable_levels()
            printer_levels_dict[printer_name] = levels_dict
        
        update_database(printer_levels_dict)

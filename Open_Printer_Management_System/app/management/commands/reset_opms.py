from django.core.management.base import BaseCommand

from app.models import Printer

class Command(BaseCommand):
    help = 'Updates the database with the newest toner data.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Printer.objects.all().delete()
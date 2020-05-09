from django.contrib import admin

from .models import Printer

class PrinterAdmin(admin.ModelAdmin):
    list_display = ('printer_name', 'printer_model_name', 'printer_location', 'ip_address', 'department_name')

admin.site.register(Printer, PrinterAdmin)

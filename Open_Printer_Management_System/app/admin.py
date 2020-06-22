from django.contrib import admin

from .models import Printer, TonerLevel, PrinterModel

class PrinterAdmin(admin.ModelAdmin):
    list_display = ('printer_name', 'printer_model_name', 'printer_location', 'ip_address', 'department_name')

admin.site.register(Printer, PrinterAdmin)

class TonerLevelAdmin(admin.ModelAdmin):
    list_display = ('printer_name', 'date_time', 'module_identifier', 'level')

admin.site.register(TonerLevel, TonerLevelAdmin)

class PrinterModelAdmin(admin.ModelAdmin):
    list_display = ("model_name", "module_numbers")

admin.site.register(PrinterModel, PrinterModelAdmin)

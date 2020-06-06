from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.management import call_command
from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe

from .forms import AddPrinterForm, SiteToggles
from .models import Printer, TonerLevel
from .snmp import determine_snmp_version, determine_printer_model

def homepage(request):
    show_location = True
    show_ip = True
    show_printer_model = False

    if request.method == 'GET':
        form = AddPrinterForm()
        toggles_form = SiteToggles()
    else:
        form = AddPrinterForm(request.POST)

        if form.is_valid():
            try:
                add_printer_form_function(form, request)
            except PrinterOffException:
                messages.error(request,
                    'Printer not added. Make sure you have the correct IP address for the printer and the printer is on.'
                )
                return redirect('homepage')
            except PrinterNotAddedException:
                messages.error(request, 'UNEXPECTED ERROR: Could not add printer.')
                return redirect('homepage')
            except NoSNMPDataException:
                messages.error(request, mark_safe(
                    "ERROR: Could not add printer. The printer doesn't have usable SNMP data.</br>"
                    "Printer may be too old or firmware may need to be updated."
                ))
                return redirect('homepage')
        
        toggles_form = SiteToggles(request.POST)
        if toggles_form.is_valid():
            if not toggles_form.cleaned_data['location']:
                show_location = False
            if not toggles_form.cleaned_data['ip_address']:
                show_ip = False
            if toggles_form.cleaned_data['printer_model']:
                show_printer_model = True

    all_departments = Printer.objects.filter().values('department_name').distinct()
    all_printer_objects = Printer.objects.all().order_by('department_name', 'printer_name')

    time_threshold = timezone.now() - settings.TIMEDELTA
    all_toner_levels = TonerLevel.objects.filter(date_time__gte=time_threshold).distinct().order_by('printer_name', 'module_identifier')

    clean_toner_levels = toner_level_cleanup(all_toner_levels)
    
    try:
        last_update_obj = TonerLevel.objects.filter().values('date_time').order_by('-date_time').distinct()[0]['date_time']
    except IndexError:
        last_update_obj = None

    return render(request, 'app/home.html', {
        'form': form, 'toggles_form': toggles_form,'show_location': show_location, 'show_ip': show_ip, 
        'show_printer_model': show_printer_model, 'all_departments': all_departments, 'all_printers': all_printer_objects,
        'all_toner_levels': clean_toner_levels, 'last_updated': last_update_obj
    })

def add_printer_form_function(form, request):
    printer_name = form.cleaned_data['printer_name']
    printer_location = form.cleaned_data['printer_location']
    ip_address = form.cleaned_data['ip_address']
    department_name = form.cleaned_data['department_name']

    version = determine_snmp_version(ip_address)
    if version == -1:
        raise PrinterOffException
    elif version == -2:
        raise PrinterNotAddedException

    printer_model_name = determine_printer_model(ip_address, version)
    if printer_model_name == -2:
        raise PrinterNotAddedException
    elif printer_model_name == -3:
        raise NoSNMPDataException

    Printer.objects.create(
        printer_name=printer_name,
        printer_model_name=printer_model_name,
        printer_location=printer_location,
        ip_address=ip_address,
        department_name=department_name,
        snmp_version=version
    )

    extra_data = f'-n {printer_name} -i {ip_address}'
    call_command('updatetonerdata', extra_data)

def refresh_toner(request):
    call_command('updatetonerdata')
    return redirect('homepage')

def toner_level_cleanup(all_toner_levels):
    new_all_toner_levels = list()
    printer_name = None
    module_id = None
    level = None

    for obj in all_toner_levels:
        if printer_name == obj.printer_name and module_id == obj.module_identifier and level == obj.level:
            continue
        else:
            new_all_toner_levels.append(obj)
            printer_name = obj.printer_name
            module_id = obj.module_identifier
            level = obj.level
    
    return new_all_toner_levels

class PrinterOffException(Exception):
    pass

class PrinterNotAddedException(Exception):
    pass

class NoSNMPDataException(Exception):
    pass

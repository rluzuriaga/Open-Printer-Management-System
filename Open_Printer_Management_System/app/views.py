from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.management import call_command
from django.conf import settings

from .forms import AddPrinterForm, SiteToggles
from .models import Printer, TonerLevel


def homepage(request):
    show_location = True
    show_ip = True

    if request.method == 'GET':
        form = AddPrinterForm()
        toggles_form = SiteToggles()
    else:
        form = AddPrinterForm(request.POST)

        if form.is_valid():
            run_form_function(form)
        
        toggles_form = SiteToggles(request.POST)
        if toggles_form.is_valid():
            if not toggles_form.cleaned_data['location']:
                show_location = False
            if not toggles_form.cleaned_data['ip_address']:
                show_ip = False

    all_departments = Printer.objects.filter().values('department_name').distinct()
    all_printer_objects = Printer.objects.all().order_by('department_name', 'printer_name')

    time_threshold = timezone.now() - settings.TIMEDELTA
    all_toner_levels = TonerLevel.objects.filter(date_time__gt=time_threshold)

    last_update_obj = TonerLevel.objects.filter().values('date_time').order_by('-date_time').distinct()[0]['date_time']

    return render(request, 'app/home.html', {
        'form': form, 'toggles_form': toggles_form,'show_location': show_location,
        'show_ip': show_ip, 'all_departments': all_departments, 'all_printers': all_printer_objects,
        'all_toner_levels': all_toner_levels, 'last_updated': last_update_obj
    })

def run_form_function(form):
    printer_name = form.cleaned_data['printer_name']
    printer_model_name = form.cleaned_data['printer_model_name']
    printer_location = form.cleaned_data['printer_location']
    ip_address = form.cleaned_data['ip_address']
    department_name = form.cleaned_data['department_name']

    Printer.objects.create(
        printer_name=printer_name,
        printer_model_name=printer_model_name,
        printer_location=printer_location,
        ip_address=ip_address,
        department_name=department_name
    )

    extra_data = f'-n {printer_name} -i {ip_address}'
    call_command('updatetonerdata', extra_data)

def refresh_toner(request):
    call_command('updatetonerdata')
    return redirect('homepage')

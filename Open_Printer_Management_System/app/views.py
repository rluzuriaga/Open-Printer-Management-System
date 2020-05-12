from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.management import call_command

from .forms import AddPrinterForm
from .models import Printer, TonerLevel

from datetime import timedelta

def homepage(request):
    if request.method == 'POST':
        form = AddPrinterForm(request.POST)

        if form.is_valid():
            run_form_function(form)

        return redirect('homepage')
    else:
        form = AddPrinterForm()

    all_departments = Printer.objects.filter().values('department_name').distinct()
    all_printer_objects = Printer.objects.all().order_by('department_name', 'printer_name')

    time_threshold = timezone.now() - timedelta(hours=1, minutes=2)
    all_toner_levels = TonerLevel.objects.filter(date_time__gt=time_threshold)

    return render(request, 'app/home.html', {
        'form': form, 'all_departments': all_departments,
        'all_printers': all_printer_objects, 'all_toner_levels': all_toner_levels
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

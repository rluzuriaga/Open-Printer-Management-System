from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.safestring import mark_safe

from .forms import AddPrinterForm, SiteToggles
from .models import Printer, TonerLevel
from .snmp import determine_snmp_version, determine_printer_model

def homepage(request):
    """
    Display the main page with all of the printers and their data (toners, location, IP address, and printer model).

    **Context**
        ``add_printer_form``
            Instance of the form to add a printer in the front-end interface.
        
        ``toggles_form``
            Instance of the form that changes the values of ``show_location``, ``show_ip``, and ``show_printer_model``.
        
        ``show_location``
            Boolean variable to show/hide the location data of the printers.
        
        ``show_ip``
            Boolean variable to show/hide the IP address data of the printers.
        
        ``show_printer_model``
            Boolean variable to show/hide the printer model data of the printers.
        
        ``all_departments``
            An instance of :model:`app.Printer` displaying only the distinct departments for the printers. 
        
        ``all_printers``
            An instrance of :model:`app.Printer` with all the printers ordered by ``department_name`` and ``printer_name``.
        
        ``all_toner_levels``
            An instance of :model:`app.TonerLevel` filtering by ``date_time`` using the time threshold specified in ``settings.py``, 
            distinct, and ordered by ``printer_name`` and ``module_identifier``.

        ``last_updated``
            An instance of :model:`app.TonerLevel` displaying the latest date and time the toner data was updated. If there is no toner 
            data, then the value is ``None``.
    
    **Template**
        :template:`app/home.html`
    """
    # Initial toggle switch state.
    show_location = True
    show_ip = True
    show_printer_model = False

    if request.method == 'GET':
        add_printer_form = AddPrinterForm()
        toggles_form = SiteToggles()
    else:
        add_printer_form = AddPrinterForm(request.POST)

        # if the form is complete and there are no repeated IP addresses,
        # then the add_printer_form_function will run. If the custom exceptions are raised,
        # error messages will be sent to the template and redirect to the homepages.
        if add_printer_form.is_valid():
            try:
                add_printer_form_function(add_printer_form)
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
        else:
            # Need to check if the form submitted is add_printer_form.
            # Without this check, the toggle switches stop working because Django doesn't know
            #   that the add_printer_form is not the form that is being submitted so the error
            #   message is sent and the toggle does not update.
            if "add_printer_submit" in add_printer_form.data:

                # Currently, only one error gets checked from the form (ip_address).
                # Instead of displaying the error in the form, I am displaying using messages.
                for error in add_printer_form.errors.values():
                    error = list(error)[0]
                    messages.error(request, mark_safe(
                        "ERROR: " + str(error) + "</br>Printer not added."
                    ))
                return redirect('homepage')
        
        # Controls the toggle switches to show/hide data from the printer cards.
        toggles_form = SiteToggles(request.POST)
        if toggles_form.is_valid():
            if not toggles_form.cleaned_data['location']:
                show_location = False
            if not toggles_form.cleaned_data['ip_address']:
                show_ip = False
            if toggles_form.cleaned_data['printer_model']:
                show_printer_model = True

    # Printer model objects.
    all_departments = Printer.objects.filter().values('department_name').distinct()
    all_printer_objects = Printer.objects.all().order_by('department_name', 'printer_name')

    # time_threshold is the last 'x' minutes/hours set in settings.py.
    time_threshold = timezone.now() - settings.TIMEDELTA
    all_toner_levels = TonerLevel.objects.filter(date_time__gte=time_threshold).distinct().order_by('printer_name', 'module_identifier')

    clean_toner_levels = toner_level_cleanup(all_toner_levels)
    
    # Try to get the latest date/time the toner data was updated.
    # If there is no data, which means there is no toner data yet (fresh install), 
    #   then the variable will be None.
    try:
        last_update_obj = TonerLevel.objects.filter().values('date_time').order_by('-date_time').distinct()[0]['date_time']
    except IndexError:
        last_update_obj = None

    return render(request, 'app/home.html', context={
        'add_printer_form': add_printer_form, 'toggles_form': toggles_form, 'show_location': show_location,
        'show_ip': show_ip, 'show_printer_model': show_printer_model, 'all_departments': all_departments,
        'all_printers': all_printer_objects, 'all_toner_levels': clean_toner_levels, 'last_updated': last_update_obj
    })

def refresh_toner(request):
    """
    View doesn't display any data.

    The view calls the ``updatetonerdata`` management command to update all the toner levels outside of the 
    time threshold set in ``settings.py`` then redirects back to :view:`app.homepage`.
    """
    call_command('updatetonerdata')
    return redirect('homepage')

def add_printer_form_function(form):
    """
    Function used to add the printer to the database after getting the SNMP version and printer model
    from the SNMP data.

    Args:
        form (forms.AddPrinterForm): User submitted form with printer name, printer location, IP 
        address, and department name.
    
    Returns:
        No returns.
    """
    printer_name = form.cleaned_data['printer_name']
    printer_location = form.cleaned_data['printer_location']
    ip_address = form.cleaned_data['ip_address']
    department_name = form.cleaned_data['department_name']

    # Get the SNMP version through brout force
    # If the function returns -1 that means that either the IP address is wrong or 
    #   the printer is off and the exception is raised.
    # If the function returns -2 the some unexpected error occurred and the exception is raised.
    # SNMP versions are either 1, 2, or 3.
    version = determine_snmp_version(ip_address)
    if version == -1:
        raise PrinterOffException
    elif version == -2:
        raise PrinterNotAddedException

    # Get the printer models through the SNMP data
    # If the function return is -2 then some unexpected error occurred and the exception is raised.
    # If the function return is -3 then that means that the printer doesn't have usable SNMP data
    #   so either the printer is too old or the firmware needs to be updated.
    printer_model_name = determine_printer_model(ip_address, version)
    if printer_model_name == -2:
        raise PrinterNotAddedException
    elif printer_model_name == -3:
        raise NoSNMPDataException

    # If both the version and printer model didn't raise any exceptions, then the printer
    #   will be added to the database.
    Printer.objects.create(
        printer_name=printer_name,
        printer_model_name=printer_model_name,
        printer_location=printer_location,
        ip_address=ip_address,
        department_name=department_name,
        snmp_version=version
    )

    # Calls the 'updatetonerdata' management command to have toner data saved on the database
    #   for the printer that was just added.
    extra_data = f'-n {printer_name} -i {ip_address}'
    call_command('updatetonerdata', extra_data)

def toner_level_cleanup(all_toner_levels):
    """
    Cleanup function used to create a list of QuerySet removing the repeated data.

    Args:
        all_toner_levels (TonerLevel QuerySet): QuerySet filtering by date_time using the time threshold specified in settings.py, 
            distinct, and ordered by printer_name and module_identifier.
    
    Returns:
        new_all_toner_levels (list): A list of the all_toner_levels QuerySet without the repeated data. 
    """
    new_all_toner_levels = list()
    printer_name = None
    module_id = None
    level = None

    # Iterate through the QuerySet and only if printer_name, module_id, and level aren't equal to the 
    #   queryset's printer name, module, and level, then that object get's added to the list.
    # Then the printer_name, module_id, and level will be assigned the object's equivalent.
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

# sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python3-dev
# pip install easysnmp
from django.conf import settings

import re
from easysnmp import Session
from easysnmp.exceptions import EasySNMPTimeoutError, EasySNMPConnectionError, EasySNMPNoSuchNameError, EasySNMPError

class SNMP:
    """ 

    Args:
        hostname (str): IPv4 address for the printer.
        version (int): SNMP version for the printer.

    Attributes:
        hostname (str): IPv4 address for the printer.
        version (int): SNMP version for the printer.
        session (easysnmp.Session): SNMP session for the printer with the given hostname and version.
    """
    def __init__(self, hostname, version):
        """ Initialize attributes and SNMP Session. """
        self.hostname = hostname
        self.version = version

        self.session = Session(hostname=self.hostname, community='public', version=self.version)

    def get_consumable_levels(self):
        """ Create a dictionary with the toner levels of a printer ready to update the database.

        Returns:
            cleaned_levels_dict (dict): Dictionary with the toner levels data ready 
                for updating the database.
            DICTIONARY STRUCTURE:
                {
                    'MODULE IDENTIFIER/TONER COLOR': 'LEVEL',
                    'Cyan': '13',
                    'Black': '29',
                    ...
                }
        """
        # Try to get a list of the last value of the oid by walking the supply description oid.
        # Some printers or copiers, Konica mainly, don't have the oids in in numerical order.
        # Example: .1.3.6.1.2.1.43.11.1.1.6.1.1, .1.3.6.1.2.1.43.11.1.1.6.1.4, .1.3.6.1.2.1.43.11.1.1.6.1.8
        try:
            oids = [oid.oid[-1] for oid in self.session.walk(".1.3.6.1.2.1.43.11.1.1.6.1")]
        except (SystemError, EasySNMPTimeoutError, EasySNMPConnectionError):

            # The text in this dictionary is checked in the template, so don't change it
            #   without changing the template's if statement as well.
            consumables_dict = {"Printer seems to be off": "Not on"}
            return consumables_dict                    

        consumables_dict = dict()

        for oid in oids:
            try:
                # Get the colorant name.
                # Doing this so that the supply name is only `Black` instead of `Canon GPR-55 Black Toner`
                supply_name = self.session.get(".1.3.6.1.2.1.43.12.1.1.4.1." + oid).value
            except EasySNMPNoSuchNameError:
                # In my testing, I have only gotten to this exception on a Canon copier.
                # It happens because there is no colorant name for waste toners or drum units.
                continue

            # Supply description example: `Canon GPR-55 Black Toner`
            supply_description = self.session.get(".1.3.6.1.2.1.43.11.1.1.6.1." + oid).value
            supply_max_capacity = self.session.get(".1.3.6.1.2.1.43.11.1.1.8.1." + oid).value
            supply_level = self.session.get(".1.3.6.1.2.1.43.11.1.1.9.1." + oid).value

            # Sometimes the supply description is in hexadecimal.
            # This tries to convert hex to ascii if that is the case.
            try:
                supply_description = bytes.fromhex(supply_description).decode('ascii')
            except ValueError:
                pass

            if supply_level == "-3":
                level = "OK"
            elif supply_level == "-2":
                level = "Unknown"
            else:
                level_percent = (int(supply_level) / int(supply_max_capacity)) * 100
                level = "{:.0f}".format(level_percent)

            if supply_name.upper() == "NOSUCHINSTANCE":
                consumables_dict[supply_description] = level
            else:
                consumables_dict[supply_name.title()] = level

        return consumables_dict


def determine_snmp_version(hostname):
    """ Function to get the SNMP version through brute force.
    
    The function tries to get the printer's description using version 3. If it
    fails, then try with version 2. If that fails, then try with version 1. Finally
    if that fails, then the printer may be off or the system's firmware may be too
    old to support SNMP.

    Args:
        hostname (str): IPv4 address for the printer.
    
    Returns:
        version (int): If positive, SNMP version of the printer. If negative, printer is off / unexpected error.
    """
    version = -1

    try:
        session = Session(hostname=hostname, community='public', version=3, retries=1)
        description = session.get('.1.3.6.1.2.1.1.1.0')
        version = 3
    except (EasySNMPTimeoutError, EasySNMPError):
        try:
            session = Session(hostname=hostname, community='public', version=2, retries=1)
            description = session.get('.1.3.6.1.2.1.1.1.0')
            version = 2
        except (EasySNMPTimeoutError, EasySNMPError):
            try:
                session = Session(hostname=hostname, community='public', version=1, retries=1)
                description = session.get('.1.3.6.1.2.1.1.1.0')
                version = 1
            except (SystemError, EasySNMPTimeoutError, EasySNMPConnectionError, EasySNMPError):
                version = -1

    return version

def determine_printer_model(hostname, version):
    """ Get the printer's model name from the SNMP data.

    The function tries to get the printer's model name through the SNMP data.
    It can sometimes raise a SystemError exception but I have seen it be multiple
      different errors so it returns -2 indicating that it is an unexpected error.
    If the model name is actually a string of 'NOSUCHINSTANCE', that means that the
      printer is too old and/or it needs a firmware update to have all the SNMP access.

    Args:
        hostname (str):
        version (int):
    
    Returns:
        printer_model_name (str): A string with the printer's models name retrieved
            from SNMP.
        Negative int: -2 = unspecified error.
                      -3 = SNMP data not given (printer/firmware too old).
    """
    session = Session(hostname=hostname, community='public', version=version)

    try:
        printer_model_name = session.get('.1.3.6.1.2.1.25.3.2.1.3.1').value
    except SystemError:
        return -2

    # If the SNMP data gives 'NOSUCHINSTANCE' that means that the firmware of
    #   the printer needs to be updated or the printer is too old.
    if str(printer_model_name) == "NOSUCHINSTANCE":
        return -3
    
    return printer_model_name

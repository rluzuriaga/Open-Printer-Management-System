# sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python3-dev
# pip install easysnmp
from django.conf import settings

import re
from easysnmp import Session
from easysnmp.exceptions import EasySNMPTimeoutError, EasySNMPConnectionError

class SNMP():
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
                    'PRINTER NAME': {
                        'MODULE IDENTIFIER/TONER COLOR': 'LEVEL',
                        'Cyan': '13', ...
                    },
                    '8X11_2232': {...}
                    ...
                }
        """
        # Try to get an integer of how many toners the printer has
        # If the printer is off it would raise one of the exception below and a dictionary
        #   is returned that gets used in the template to show the printer is off
        try:
            number_of_consumables = len(self.session.walk(".1.3.6.1.2.1.43.11.1.1.6.1"))
        except (SystemError, EasySNMPTimeoutError, EasySNMPConnectionError):

            # The text in this dictionay is checked in the template, so don't change it
            #   without changing the template's if statement as well.
            consumables_dict = {"Printer seems to be off": "Not on"}
            return consumables_dict                    

        consumables_dict = dict()

        # Iterate through each toner/module and add the colorant, capacity, and level
        #   of each one in the consumables_dict.
        for i in range(1, number_of_consumables + 1):
            # The full toner/module name
            key = self.session.get(".1.3.6.1.2.1.43.11.1.1.6.1." + str(i)).value
            
            consumables_dict[key] = dict()

            # Integer with the SNMP value of the toner/module, used to get the plain module name without extra data
            consumables_dict[key]['colorant'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.3.1." + str(i)).value

            consumables_dict[key]['capacity'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.8.1." + str(i)).value
            consumables_dict[key]['level'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.9.1." + str(i)).value

        # Cleanup the dictionary data to make it ready to update the database
        cleaned_levels_dict = self._data_cleanup(consumables_dict)

        return cleaned_levels_dict

    def _data_cleanup(self, uncleaned_dict):
        """ Internal function to clean a dictionary and make it the format to easily update the database.
        
        Args:
            uncleaned_dict (dict): Dictionary with uncleaned printer toner data retrieved from SNMP.
            DICTIONARY STRUCTURE:
            {
                'FULL MODULE NAME': {
                    'colorant': 'INTEGER',
                    'capacity': 'INTEGER',
                    'level': 'INTEGER'
                },
                'Black Cartridge 508A HP CF360A\x00': {
                    'colorant': '1',
                    'capacity': '100',
                    'level': '38'
                }
            }
        
        Returns:
            cleaned_levels_dict (dict): Dictionary with cleaned printer toner data formated in a way that can be easily 
                used to update the database.
            DICTIONARY STRUCTURE:
            {
                'PRINTER NAME': {
                    'MODULE IDENTIFIER/TONER COLOR': 'LEVEL',
                    'Cyan': '13', ...
                },
                '8X11_2232': {...}
                ...
            }
        """
        cleaned_levels_dict = dict()

        for full_module_name, toner_data_dict in uncleaned_dict.items():
            capacity = None
            level = None
            colorant = None

            # Iterate through the toner data dictionary to create the capacity, colorant,
            #   and level variables.
            for key, value in toner_data_dict.items():
                if key == 'capacity':
                    capacity = value
                elif key == 'level':
                    level = value
                elif key == 'colorant':
                    colorant = value
            
            # Get the toner/module name from the printer's SNMP data using the colorant's value.
            module_name = self.session.get(".1.3.6.1.2.1.43.12.1.1.4.1." + str(colorant)).value
            
            # Some printer's fimware doesn't have a value for for the module name when trying to
            #   get it from the colorant, outputing 'NOSUCHINSTANCE'.
            # If that value is given so then the module name falls back to the full_module_name
            #   but needs to be cleaned from extra data.
            if module_name == "NOSUCHINSTANCE":
                module_name = full_module_name
            else:
                # This regex code is here because some of the module names appear like this
                #   'photoBlack', so the regex just seperates the words to then be capitalized.
                module_name = re.sub(r"(\w)([A-Z])", r"\1 \2", module_name)
                module_name = module_name.title()
            
            # Some values return a unicode null value at the end of the string, so this removes it.
            module_name = module_name.replace(u'\x00', '')

            # SNMP returns some specific values for "OK" and "NA", so this checks for those values
            #   in level.
            # If the value is not "OK" or "NA", then the percentage is calculated by dividing level
            #   by capacity then multiplying by 100.
            if str(level) == '-3':
                cleaned_levels_dict[module_name] = 'OK'
            elif str(level) == '-2':
                cleaned_levels_dict[module_name] = 'NA'
            else:
                level_percentage = float(level) / float(capacity) * 100

                # This string format removes the decimal value after the percentage
                cleaned_levels_dict[module_name] = "{:.0f}".format(level_percentage)

        return cleaned_levels_dict


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
        session = Session(hostname=hostname, community='public', version=3)
        description = session.get('.1.3.6.1.2.1.1.1.0')
        version = 3
    except SystemError as error:
        if "returned NULL without setting an error" in str(error):
            try:
                session = Session(hostname=hostname, community='public', version=2)
                description = session.get('.1.3.6.1.2.1.1.1.0')
                version = 2
            except SystemError as error:
                if "returned NULL without setting an error" in str(error):
                    try:
                        session = Session(hostname=hostname, community='public', version=1)
                        description = session.get('.1.3.6.1.2.1.1.1.0')
                        version = 1
                    except (SystemError, EasySNMPTimeoutError, EasySNMPConnectionError):
                        version = -1
                else:
                    version = -2
        else:
            version = -2
    
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

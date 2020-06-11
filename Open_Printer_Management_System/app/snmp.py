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
        self.hostname = hostname
        self.version = version

        self.session = Session(hostname=self.hostname, community='public', version=self.version)

    def get_consumable_levels(self):
        """ Create a dictionary with the toner levels of a printer ready to update the database.

        Returns:
            cleaned_levels_dict (dict): Dictionary with the toner levels data ready 
                for updating the database.
        """
        # Try to get an integer of how many toners the printer has
        # If the printer is off it would raise one of the below exception and a dictionary
        #   is returned that gets used in the template to show the printer is off
        try:
            number_of_consumables = len(self.session.walk(".1.3.6.1.2.1.43.11.1.1.6.1"))
        except (SystemError, EasySNMPTimeoutError, EasySNMPConnectionError):

            # The text in this dictionay is checked in the template, so don't change it
            #   without changing the template if statement as well.
            consumables_dict = {"Printer seems to be off": "Not on"}
            return consumables_dict                    

        consumables_dict = dict()

        # Iterate through each toner/module and add the colorant, capacity, and level
        #   of each one in the consumables_dict.
        for i in range(1, number_of_consumables + 1):
            # The toner/module name
            key = self.session.get(".1.3.6.1.2.1.43.11.1.1.6.1." + str(i)).value
            
            consumables_dict[key] = dict()

            # Integer with the SNMP value of the toner/module
            consumables_dict[key]['colorant'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.3.1." + str(i)).value

            consumables_dict[key]['capacity'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.8.1." + str(i)).value
            consumables_dict[key]['level'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.9.1." + str(i)).value

        # Cleanup the data to make it ready to update the database
        cleaned_levels_dict = self._data_cleanup(consumables_dict)

        return cleaned_levels_dict

    def _data_cleanup(self, uncleaned_dict):
        """ Internal function to clean a dictionary and make it the format to easily update the database.
        
        Args:
            uncleaned_dict (dict):
        
        Returns:
            levels_dict (dict):
        """
        levels_dict = dict()

        for key_top, value_dict in uncleaned_dict.items():
            capacity = None
            level = None
            colorant = None

            for key, value in value_dict.items():
                if key == 'capacity':
                    capacity = value
                elif key == 'level':
                    level = value
                elif key == 'colorant':
                    colorant = value
            
            # Key cleanup
            module_name = self.session.get(".1.3.6.1.2.1.43.12.1.1.4.1." + str(colorant)).value
            
            if module_name == "NOSUCHINSTANCE":
                module_name = key_top.rstrip('\x00')
            else:
                module_name = re.sub(r"(\w)([A-Z])", r"\1 \2", module_name)
                module_name = module_name.title()


            # Level Cleanup
            if str(level) == '-3':
                levels_dict[module_name] = 'OK'
            elif str(level) == '-2':
                levels_dict[module_name] = 'NA'
            else:
                level_percentage = float(level) / float(capacity) * 100
                levels_dict[module_name] = "{:.0f}".format(level_percentage)

        return levels_dict


def determine_snmp_version(hostname):
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
                    except SystemError:
                        return -1
                else:
                    return -2
        else:
            return -2
    
    return version

def determine_printer_model(hostname, version):
    session = Session(hostname=hostname, community='public', version=version)
    try:
        printer_model_name = session.get('.1.3.6.1.2.1.25.3.2.1.3.1').value
    except SystemError:
        return -2

    if str(printer_model_name) == "NOSUCHINSTANCE":
        return -3
    
    return printer_model_name

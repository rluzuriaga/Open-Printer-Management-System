# sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python3-dev
# pip install easysnmp

import re
from easysnmp import Session
from easysnmp.exceptions import EasySNMPTimeoutError

class SNMP():
    def __init__(self, hostname):
        self.hostname = hostname

        self.session = Session(hostname=self.hostname, community='public', version=3)

    def get_consumable_levels(self):
        try:
            consumable_number = len(self.session.walk(".1.3.6.1.2.1.43.11.1.1.6.1"))
        except (SystemError, EasySNMPTimeoutError):
            try:
                self.session = Session(hostname=self.hostname, community='public', version=2)
                consumable_number = len(self.session.walk(".1.3.6.1.2.1.43.11.1.1.6.1"))
            except (SystemError, EasySNMPTimeoutError):
                self.session = Session(hostname=self.hostname, community='public', version=1)
                consumable_number = len(self.session.walk(".1.3.6.1.2.1.43.11.1.1.6.1"))

        res = dict()

        for i in range(1, consumable_number + 1):
            key = self.session.get(".1.3.6.1.2.1.43.11.1.1.6.1." + str(i)).value
            res[key] = dict()

            res[key]['colorant'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.3.1." + str(i)).value

            res[key]['class'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.4.1." + str(i)).value
            res[key]['type'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.5.1." + str(i)).value

            res[key]['units'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.7.1." + str(i)).value
            res[key]['capacity'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.8.1." + str(i)).value
            res[key]['level'] = self.session.get(".1.3.6.1.2.1.43.11.1.1.9.1." + str(i)).value

        # Cleanup the data
        cleaned_levels_dict = self._data_cleanup(res)

        return cleaned_levels_dict

    def _data_cleanup(self, uncleaned_dict):
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
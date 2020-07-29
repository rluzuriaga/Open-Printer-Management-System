from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

import os
import sys
from subprocess import check_call, CalledProcessError


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = BASE_DIR + '/Open_Printer_Management_System/Open_Printer_Management_System/settings.py'
PYTHON_VENV_PATH = BASE_DIR + '/venv/bin/python'
PYTHON_PATH = '/usr/bin/python3'

PRECREATED_DATABASE = False
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_NAME = None
DATABASE_USERNAME = None
DATABASE_PASSWORD = None
DATABASE_HOST = None
DATABASE_PORT = None

TIMEZONE = None

DEFAULT_TIMEDELTA = False
TIMEDELTA_HOURS = 0
TIMEDELTA_MINUTES = 10

class UserDefinedSettings:
    def __init__(self):
        self.use_default_database = True
        self.database_engine = None
        self.database_name = None
        self.database_username = None
        self.database_password = None
        self.database_host = None
        self.database_port = None

        self.use_default_timezone = True
        self.timezone = 'America/Los_Angeles'

        self.use_default_timedelta = True
        self.timedelta_hours = 0
        self.timedelta_minutes = 10

        self.get_database_data()
        self.get_timezone_data()
        self.get_timedelta_data()

        # Added these here to make it not repeated
        if not self.use_default_database:
            DATABASE_ENGINE = self.database_engine
            DATABASE_NAME = self.database_name
            DATABASE_USERNAME = self.database_username
            DATABASE_PASSWORD = self.database_password
            DATABASE_HOST = self.database_host
            DATABASE_PORT = self.database_port
        
        TIMEZONE = self.timezone

        TIMEDELTA_HOURS = self.timedelta_hours
        TIMEDELTA_MINUTES = self.timedelta_minutes

    def _user_entered_database_inputs(self):
        self.database_name = input("Please enter the database's name: ").strip()
        self.database_username = input("Please enter the username for the database: ").strip()
        self.database_password = input("Please enter the password for that user: ").strip()
        self.database_host = input("Please enter the host for the database: ").strip()
        self.database_port = input("Please enter the database port: ").strip()

    def get_database_data(self):
        print(
            "\n\n\n\n------------------------------------------------------------------------------------------\n\n"
            "What database engine would you like to use?\n"
            "    The default database is SQLite.\n"
        )

        input_use_default_database = input("Do you want to use the default database? [Y/n] ")

        if input_use_default_database.lower().strip() == 'y' or input_use_default_database.strip() == '':
            print("\nThe default database will be used.")
            self.database_engine = 'django.db.backends.sqlite3'
        elif input_use_default_database.lower().strip() == 'n':
            self.use_default_database = False
        else:
            print("The input entered is not valid. Exiting.")
            sys.exit(1)
        
        if not self.use_default_database:
            print(
                "\n\n  1. PostgreSQL\n"
                "  2. MySQL\n"
                "  3. Oracle (You will need to setup the database yourself)\n"
            )

            input_database_selection = input("Please enter the number next to the database you would like to use: ")

            try:
                input_database_selection = int(input_database_selection)
            except ValueError:
                print("The input is not a number. Exiting.")
                sys.exit(1)
            
            if input_database_selection == 1 or input_database_selection == 2:
                precreated_database = input("Do you have a database already created? [y/N] ")

                if precreated_database.lower().strip() == 'y':
                    print("\nYou will be asked the database name, username with access to that database, host address, and port.")
                    self._user_entered_database_inputs()
                    PRECREATED_DATABASE = True

                elif precreated_database.lower().strip() == 'n' or precreated_database.strip() == '':
                    print("\nThe database will be automatically created.")

                    if input_database_selection == 1:
                        self.database_engine = 'django.db.backends.postgresql'
                        self.database_port = '5432'
                    elif input_database_selection == 2:
                        self.database_engine = 'django.db.backends.mysql'
                        self.database_port = '3306'
                    
                    self.database_name = 'open_printer_management_system'
                    self.database_username = 'open_printer_management_system_user'
                    self.database_password = '!Open_Printer_Management_System_P@ssword!'
                    self.database_host = '127.0.0.1'
                else:
                    print("The input entered is not valid. Exiting.")
                    sys.exit(1)
            elif input_database_selection == 3:
                print(
                    "Make sure you already have your Oracle SQL database setup.\n"
                    "If you don't have this setup, you can use 'Ctrl + C' to exit the program and setup your database.\n"
                    "You will be asked the database name, username with access to that database, host address, and port.\n\n"
                )

                self._user_entered_database_inputs()
                
            else:
                print("The input entered is not valid. Exiting.")
                sys.exit(1)

    def get_timezone_data(self):
        print(
            "\n\n------------------------------------------------------------------------------------------\n\n"
            "The system needs a timezone.\n"
            "    The default is 'America/Los_Angeles'.\n"
            "    If you are going to use a different timezone, please use the 'TZ database name' column from 'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones' for your timezone.\n"
        )

        input_use_default_timezone = input("Do you want to use the default timezone? [Y/n] ")

        if input_use_default_timezone.lower().strip() == 'y' or input_use_default_timezone.strip() == '':
            print("The default timezone will be used.")
        elif input_use_default_timezone.lower().strip() == 'n':
            self.use_default_timezone = False
        else:
            print("The input entered is not valid. Exiting.")
            sys.exit(1)

        if not self.use_default_timezone:
            input_timezone = input("Please enter your timezone: ")

            input_timezone = input_timezone.replace("'", "").replace('"', '').replace('\n', '').strip()

            import pytz
            if input_timezone not in pytz.all_timezones:
                print("Invalid timezone. Exiting.")
                sys.exit(1)
            else:
                self.timezone = input_timezone

    def get_timedelta_data(self):
        print(
            "\n\n------------------------------------------------------------------------------------------\n\n"
            "How often would you want the system to update the printer's toner data in the background?\n"
            "    The default is to update the toner data every 10 minutes.\n"
        )

        input_use_default_timedelta = input("Do you want to use the default time? [Y/n] ")

        if input_use_default_timedelta.lower().strip() == 'y' or input_use_default_timedelta.strip() == '':
            print("The default time for updating the toner data will be used.")
            DEFAULT_TIMEDELTA = True
        elif input_use_default_timedelta.lower().strip() == 'n':
            self.use_default_timedelta = False
        else:
            print("The input entered is not valid. Exiting.")
            sys.exit(1)

        if not self.use_default_timedelta:
            print(
                "Please enter a number next to 'Hours: ' and/or 'Minutes: '\n"
                "    Examples:\n"
                "            Hours:   1                OR                Hours:   0\n"
                "            Minutes: 0                OR                Minutes: 30\n"
                "      Every hour on the hour                Every 30th minute (1:00, 1:30, 2:00...)\n\n"

                "    Please note that if entering a minute value that isn't equally divisible by 60 and/or an hour value that isn't equally divisible by 24, the toner update job will also be ran at the 0th minute (every hour on the hour) and/or at midnight respectively.\n"
                "    Examples: \n"
                "           Every 18 minutes (1:00, 1:18, 1:36, 1:54, 2:00...)        OR     Every 45 minutes (1:00, 1:45, 2:00, 2:45...)\n"
                "           Every 7 hours (00:00, 7:00, 14:00, 21:00, 00:00...)       OR     Every 15 hours (00:00, 15:00, 00:00, 15:00 ...)\n"
                "           Every 7 hours and 18 minutes (21:00, 21:18, 21:36, 21:54, 00:00, 00:18 ... 7:00, 7:18 ... 14:00, 14:18 ...)\n\n"
            )

            input_hours = input("Hours:   ")
            input_minutes = input("Minutes: ")

            try:
                input_hours = int(input_hours)
                input_minutes = int(input_minutes)
            except ValueError:
                print("One or more entered inputs were not numbers. Exiting.")
                sys.exit(1)
            
            if input_hours < 0 or input_minutes < 0:
                print("One or more entered inputs were not positive numbers. Exiting.")
                sys.exit(1)
            
            if input_hours == 0 and input_minutes < 5:
                print("The minimum time value is every 5 minutes. Setting the update toner time to every 5 minutes.")
                input_hours = 0
                input_minutes = 5

            self.timedelta_hours = input_hours
            self.timedelta_minutes = input_hours

class InstallCommand(install):
    """Pre-installation for installation mode."""
    def run(self):
        check_call("sudo apt update".split())
        check_call("sudo apt install libsnmp-dev snmp-mibs-downloader python3-dev gcc nginx -y".split())
        check_call("pip3 install pytz".split())

        user_defined_settings = UserDefinedSettings()

        if 'postgresql' in user_defined_settings.database_engine:
            check_call("sudo apt install postgresql postgresql-contrib -y".split())
            check_call("pip3 install psycopg2-binary".split())

            # Start and enable PostgreSQL
            try:
                check_call("sudo systemctl start postgresql".split())
                check_call("sudo systemctl enable postgresql".split())
            except CalledProcessError:
                try:
                    check_call("sudo service postgresql start".split())
                except CalledProcessError:
                    print(
                        "\n\nERROR: Could not start and enable PostgeSQL.\n"
                        "Please use the command 'sudo systemctl start postgresql && sudo systemctl enable postgresql', then run the install command again. Exiting."
                    )
                    sys.exit(1)

        elif 'mysql' in user_defined_settings.database_engine:
            check_call("sudo apt install mysql-server libmysqlclient-dev default-libmysqlclient-dev -y".split())
            check_call("pip3 install mysqlclient".split())

            # Start and enable MySQL
            try:
                check_call("sudo systemctl start mysql".split())
                check_call("sudo systemctl enable mysql".split())
            except CalledProcessError:
                try:
                    check_call("sudo service mysql start".split())
                except CalledProcessError:
                    print(
                        "\n\nERROR: Could not start and enable MySQL.\n"
                        "Please use the command 'sudo systemctl start mysql && sudo systemctl enable mysql', then run the install command again. Exiting."
                    )
                    sys.exit(1)
        
        elif 'oracle' in user_defined_settings.database_engine:
            check_call("pip3 install cx_Oracle".split())


        ####### Actually run the setup() at the bottom of this script
        install.run(self)
        #######


        # Post setup() commands

        check_call(f"pip3 install -e {BASE_DIR}".split())

        # Create databases for PostgreSQL or MySQL !IF! that is what the user 
        if not PRECREATED_DATABASE:
            if 'postgresql' in DATABASE_ENGINE:
                print("Creating PostgreSQL Database")
                check_call(["sudo", "-u", "postgres", "psql", "-c", f"CREATE DATABASE {DATABASE_NAME};"])
                check_call(["sudo", "-u", "postgres", "psql", "-c", f"CREATE USER {DATABASE_USERNAME} WITH PASSWORD '{DATABASE_PASSWORD}';"])
                check_call(["sudo", "-u", "postgres", "psql", "-c", f"ALTER ROLE {DATABASE_USERNAME} SET client_encoding TO 'utf8';"])
                check_call(["sudo", "-u", "postgres", "psql", "-c", f"ALTER ROLE {DATABASE_USERNAME} SET default_transaction_isolation TO 'read committed';"])
                check_call(["sudo", "-u", "postgres", "psql", "-c", f"ALTER ROLE {DATABASE_USERNAME} SET timezone TO '{TIMEZONE}';"])
                check_call(["sudo", "-u", "postgres", "psql", "-c", f"GRANT ALL PRIVILEGES ON DATABASE {DATABASE_NAME} TO {DATABASE_USERNAME};"])
            
            elif 'mysql' in DATABASE_ENGINE:
                check_call(["sudo", "mysql", "-u", "root", "-Bse", f"CREATE DATABASE {DATABASE_NAME};"])
                check_call(["sudo", "mysql", "-u", "root", "-Bse", f"CREATE USER '{DATABASE_USERNAME}'@'%' IDENTIFIED WITH mysql_native_password BY '{DATABASE_PASSWORD}';"])
                check_call(["sudo", "mysql", "-u", "root", "-Bse", f"GRANT ALL ON {DATABASE_NAME}.* TO '{DATABASE_USERNAME}'@'%';"])
                check_call(["sudo", "mysql", "-u", "root", "-Bse", "FLUSH PRIVILEGES;"])
        
        
        # Run the collect static command
        try:
            check_call(f"{PYTHON_VENV_PATH} {BASE_DIR}/Open_Printer_Management_System/manage.py collectstatic".split())
        except FileNotFoundError:
            check_call(f"{PYTHON_PATH} {BASE_DIR}/Open_Printer_Management_System/manage.py collectstatic".split())


        # Edit settings.py file

        # !!IMPORTANT!! - The spacing for these strings need to stay how they are
        database_info = \
            "DATABASES = {\n"\
            "    'default': {\n"\
            f"        'ENGINE': '{DATABASE_ENGINE}',\n"\
            f"        'NAME': '{DATABASE_NAME}',\n"\
            f"        'USER': '{DATABASE_USERNAME}',\n"\
            f"        'PASSWORD': '{DATABASE_PASSWORD}',\n"\
            f"        'HOST': '{DATABASE_HOST}',\n"\
            f"        'PORT': '{DATABASE_PORT}'\n"\
            "    }\n"\
            "}\n"

        # Read through the settings file
        with open(SETTINGS_FILE, 'r') as f:
            settings_lines = f.readlines()
        
        # Overwrite the settings.py file with new data
        with open(SETTINGS_FILE, 'w') as f:

            for line in settings_lines:
                # Change database info if not using the default database
                if 'DATABASES = {' in line:
                    if 'sqlite3' not in DATABASE_ENGINE:
                        f.write(database_info)
                        continue
                
                # Change timezone data if not using default
                elif 'TIME_ZONE = ' in line: 
                    if TIMEZONE != 'America/Los_Angeles':
                        f.write(f"TIME_ZONE = '{TIMEZONE}'")
                        continue
                
                # Change the static files code to contain STATICFILES_DIRS instead of STATIC_ROOT
                elif 'STATIC_ROOT = ' in line:
                    f.write("STATICFILES_DIRS = [\n    os.path.join(BASE_DIR, 'static'),\n]\n")
                    continue
                
                # Change the timedelta info if not using the default
                elif 'TIMEDELTA = timedelta' in line:
                    if not DEFAULT_TIMEDELTA:
                        f.write(f"TIMEDELTA = timedelta(hours={int(TIMEDELTA_HOURS)}, minutes={int(TIMEDELTA_MINUTES)})")
                        continue
                
                # If the line isn't one that needs to be changed then the line is just written to the file
                else:
                    f.write(line)
                    # new_settings_lines.append(line)
        

        # Create crontab file
        crontab_text = ""
        if TIMEDELTA_MINUTES == 0:
            crontab_text += "0 "
        else:
            crontab_text += f"*/{TIMEDELTA_MINUTES} "
        
        if TIMEDELTA_HOURS == 0 or TIMEDELTA_HOURS == 1:
            crontab_text += "* "
        else:
            crontab_text += f"*/{TIMEDELTA_HOURS} "
        
        crontab_text += f"* * * {BASE_DIR}/updatetonerdata.sh"

        with open(BASE_DIR + "/crontab_updatetonerdata", 'w') as f:
            f.write(crontab_text)


        # Modify updatetonerdata.sh
        with open(BASE_DIR + "/updatetonerdata.sh", 'r') as f:
            update_toner_data_lines = f.readlines()
        
        with open(BASE_DIR + "/updatetonerdata.sh", 'w') as f:
            for line in update_toner_data_lines:
                if 'PROJECT_PATH=' in line:
                    f.write(f"PROJECT_PATH={BASE_DIR}\n")
        

        # Activate crontab
        check_call(f"crontab < {BASE_DIR}/crontab_updatetonerdata".split())        

setup(
    name='Open-Printer-Management-System',
    version='1.1.0',
    description='Django project to easily view and manage printer SNMP data.',
    url='https://github.com/rluzuriaga/Open-Printer-Management-System',
    license='MIT',
    author='Rodrigo Luzuriaga',
    author_email='me@rodrigoluzuriaga.com',
    maintainer='Rodrigo Luzuriaga',
    maintainer_email='me@rodrigoluzuriaga.com',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'django>=3.0,<4.0',
        'easysnmp>=0.2.5,<0.3.0',
        'gunicorn>=20.0,<21'
    ],
    cmdclass={
        'install': InstallCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server'
    ]
)
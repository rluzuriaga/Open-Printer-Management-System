#!/bin/bash

# Hacky way of asking the user to input the sudo password first
sudo echo ""

# # User defined/selection for database
use_default_database_func() {
    echo -e "------------------------------------------------------------------------------------------\n"
    echo "What database engine would you like to use?"
    echo -e "    The default database is SQLite.\n"

    while true; do
        read -p "Do you want to use the default database? [Y/n] " default_database
        if [[ -z "$default_database" ]]; then
            return
        fi

        case "$default_database" in
            Y*|y* ) return;;
            N*|n* ) break;;
            * ) echo -e "Please enter either 'y' or 'n' only.\n";
        esac
    done

    false
}

get_database_data() {
    while true; do
        echo -e "\n  1. PostgreSQL"
        echo -e "  2. MySQL\n"
        # Setting will be included in the future
        # echo "  3. Oracle (You will need to setup the database yourself.)\n"

        read -p "Please enter the number next to the database you would like to use: " database_selection

        case "$database_selection" in
            1 ) database_engine="django.db.backends.postgresql"; database_port="5432"; break;;
            2 ) database_engine="django.db.backends.mysql"; database_port="3306"; break;;
            # 3 )
            * ) echo -e "The input entered is not valid. Please enter the correct number for the database you want to use.\n"
        esac
    done

    database_name="open_printer_management_system"
    database_username="open_printer_management_system_user"
    database_password="0pen_Pr1nter_M@n@gement_System_P@ssw0rd"
    database_host="127.0.0.1"
}

replace_database_info_on_settings() {
    original_database_data="DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),}}"
    
    new_database_data="DATABASES = {\n    'default': {\n        'ENGINE': '$database_engine',\n        'NAME': '$database_name',\n        'USER': '$database_username',\n        'PASSWORD': '$database_password',\n        'HOST': '$database_host',\n        'PORT': '$database_port'\n    }\n}"

    sed -i -e "s/${original_database_data}*/${new_database_data}/g" Open_Printer_Management_System/Open_Printer_Management_System/settings.py
}

# Get the database info from user.
# If the user wants to use the default database (SQLite3), then nothing will be changed on settings.py
# If the user doesn't want to use the default database, then they will be asked what database they want to use and then the database info will be changed in settings.py.
if ! use_default_database_func; then
    # Ask the user what database engine they want to use
    get_database_data

    # Replace the database info in settings.py
    replace_database_info_on_settings
else
    echo -e "The default database will be used.\n"
fi



# # User defined/selection of timezone
use_default_timezone_func() {
    echo -e "\n\n------------------------------------------------------------------------------------------\n"
    echo "The system needs a timezone."
    echo "    The default is 'America/Los_Angeles'."
    echo -e "    If you are going to use a different timezone, please use the 'TZ database name' column from 'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones' for your timezone.\n"

    while true; do
        read -p "Do you want to use the default timezone? [Y/n] " default_timezone
        if [[ -z "$default_timezone" ]]; then
            timezone_data="America/Los_Angeles"
            return
        fi

        case "$default_timezone" in
            Y*|y* ) return;;
            N*|n* ) break;;
            * ) echo -e "Please enter either 'y' or 'n' only.\n";
        esac
    done
    
    false
}
get_timezone_user_input() {
    while true; do
        read -p "Please enter your timezone: " timezone_input

        if [[ -e /usr/share/zoneinfo/$timezone_input ]]; then
            timezone_data=$timezone_input
            break
        else
            echo -e "\nThe timezone entered is not valid. Make sure you entered the correct timezone without any spaces or special characters."
        fi
    done
}

replace_timezone_info_on_settings() {
    original_timezone_data="TIME_ZONE = 'America/Los_Angeles'"
    new_timezone_data="TIMEZONE = '$1'"

    sed -i -e "s~${original_timezone_data}~${new_timezone_data}~g" Open_Printer_Management_System/Open_Printer_Management_System/settings.py
}

# Get the timezone info from the user.
# If the user selects to use the default, then nothing will be changed on settings.py
# If the user selects to not use the default timezone, then they will need to enter a timezone, the function will check if it is a valid timezone and then change settings.py to use that timezone.
if ! use_default_timezone_func; then
    # Ask the user to enter the timezone they want to use and check if it is valid.
    get_timezone_user_input

    # Replace the timezone info in settings.py
    replace_timezone_info_on_settings ${timezone_data}
else
    echo -e "The default timezone will be used.\n"
fi



# # User defined/selection of timedelta
use_default_timedelta_func() {
    echo -e "\n\n------------------------------------------------------------------------------------------\n"
    echo "How often would you want the system to update the printer's toner data in the background?"
    echo "    The default is to update the toner data every 10 minutes.\n"

    while true; do
        read -p "Do you want to use the default time? [Y/n] " default_timedelta
        if [[ -z "$default_timedelta" ]]; then
            return
        fi

        case "$default_timedelta" in
            Y*|y* ) return;;
            N*|n* ) break;;
            * ) echo -e "Please enter either 'y' or 'n' only.\n";
        esac
    done

    false
}

get_timedelta_user_input() {
    echo -e "\n    Examples:"
    echo "            Hours:   1                OR                Hours:   0"
    echo "            Minutes: 0                OR                Minutes: 30"
    echo -e "      Every hour on the hour                Every 30th minute (1:00, 1:30, 2:00...)\n"

    echo "    Please note that if entering a minute value that isn't equally divisible by 60 and/or an"
    echo "     hour value that isn't equally divisible by 24, the toner update job will also be ran at"
    echo -e "     the 0th minute (every hour on the hour) and/or at midnight respectively.\n"
    echo "    Examples: "
    echo "           Every 18 minutes (1:00, 1:18, 1:36, 1:54, 2:00...)        OR     Every 45 minutes (1:00, 1:45, 2:00, 2:45...)"
    echo "           Every 7 hours (00:00, 7:00, 14:00, 21:00, 00:00...)       OR     Every 15 hours (00:00, 15:00, 00:00, 15:00 ...)"
    echo -e "           Every 7 hours and 18 minutes (21:00, 21:18, 21:36, 21:54, 00:00, 00:18 ... 7:00, 7:18 ... 14:00, 14:18 ...)\n"

    echo -e "\nPlease enter a number next to 'Hours: ' and 'Minutes: '. The minimum time value is every 5 minutes."

    while true; do
        read -p "Hours: " hours_input

        case $hours_input in 
            0|1|2|3|4|5|6|7|8|9|1[0-9]|2[0-4] ) timedelta_hours=$hours_input; break;;
            * ) echo -e "Please enter a valid hour value.\n"
        esac
    done

    while true; do
        read -p "Minutes: " minutes_input

        case $minutes_input in
            0|1|2|3|4 ) 
                if [[ $timedelta_hours -eq 0 ]]; then 
                    echo -e "You can't have a value less than 5 minutes.\nPlease enter a valid minute value.\n";
                else
                    timedelta_minutes=$minutes_input; 
                    break;
                fi;;
            5|6|7|8|9|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9] ) timedelta_minutes=$minutes_input; break;;
            * ) echo -e "Please enter a valid minute value.\n"
        esac
    done
}

replace_timedlta_info_on_settings() {
    local timedelta_hours=$1
    local timedelta_minutes=$2

    original_timedelta_data="TIMEDELTA = timedelta(minutes=10)"
    new_timedelta_data="TIMEDELTA = timedelta(hours=$timedelta_hours, minutes=$timedelta_minutes)"

    sed -i -e "s~${original_timedelta_data}~${new_timedelta_data}~g" Open_Printer_Management_System/Open_Printer_Management_System/settings.py
}

# Get the timedelta info from the user.
# If the user selects to use the default, then nothing will be changed on settings.py
# If the user selects to not use the default timedelta, then they will need to enter a hour and minute value, the function will check if it is valid and then change settings.py to use that timedelta.
if ! use_default_timedelta_func; then
    # Ask the user to enter the timedelta they want to use and check if it is valid.
    get_timedelta_user_input

    # Replace the timedelta info in settings.py
    replace_timedlta_info_on_settings $timedelta_hours $timedelta_minutes
else
    echo "The default time for updating the toner data will be used. (Every 10 minutes)"
fi



# # Start of Linux package installs
current_directory=$PWD
if [[ -z "$SUDO_USER" ]]; then
    username=$USER
else
    username=$SUDO_USER
fi

# Create Python3 virtual environment
{
    python3 -m venv $current_directory/venv
} || {
    sudo apt install python3-venv -y
    python3 -m venv $current_directory/venv
}


sudo apt update
sudo apt install libsnmp-dev snmp-mibs-downloader python3-dev gcc nginx curl -y

if [[ $database_engine == "django.db.backends.postgresql" ]]; then

    # Install the PostgreSQL Python package
    $current_directory/venv/bin/python3 -m pip install psycopg2-binary

    # Install, start, and enable PostgreSQL
    sudo apt install postgresql postgresql-contrib -y
    sudo systemctl start postgresql && sudo systemctl enable postgresql || sudo service postgresql start

    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE $database_name;"
    sudo -u postgres psql -c "CREATE USER $database_username WITH PASSWORD '$database_password';"
    sudo -u postgres psql -c "ALTER ROLE $database_username SET client_encoding TO 'utf8';"
    sudo -u postgres psql -c "ALTER ROLE $database_username SET default_transaction_isolation TO 'read committed';"
    sudo -u postgres psql -c "ALTER ROLE $database_username SET timezone TO '$timezone_data';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $database_name TO $database_username;"
    
elif [[ $database_engine == "django.db.backends.mysql" ]]; then

    # Install the MySQL package needed for Python
    $current_directory/venv/bin/python3 -m pip install mysqlclient

    # Install, start, and enable MySQL
    sudo apt install mysql-server libmysqlclient-dev default-libmysqlclient-dev -y
    sudo systemctl start mysql && sudo systemctl enable mysql || sudo service mysql start

    # Create database and user
    sudo mysql -u root -Bse "CREATE DATABASE $database_name;"
    sudo mysql -u root -Bse "CREATE USER '$database_username'@'%' IDENTIFIED WITH mysql_native_password BY '$database_password';"
    sudo mysql -u root -Bse "GRANT ALL ON $database_name.* TO '$database_username'@'%';"
    sudo mysql -u root -Bse "FLUSH PRIVILEGES;"
    
fi

# Install setup.py
$current_directory/venv/bin/python3 -m pip install $current_directory

# Django specific commands
$current_directory/venv/bin/python3 $current_directory/Open_Printer_Management_System/manage.py makemigrations
$current_directory/venv/bin/python3 $current_directory/Open_Printer_Management_System/manage.py migrate
$current_directory/venv/bin/python3 $current_directory/Open_Printer_Management_System/manage.py collectstatic --noinput

# Change static files code in settings.py
original_static_data="STATIC_ROOT = os.path.join(BASE_DIR, 'static')"
new_static_data="STATICFILES_DIRS = [\n    os.path.join(BASE_DIR, 'static'),\n]\n"

sed -i -e "s~${original_static_data}~${new_static_data}~g" Open_Printer_Management_System/Open_Printer_Management_System/settings.py

# Create crontab file
crontab_text=""
if [[ $timedelta_minutes -eq 0 || $timedelta_minutes == "0" ]]; then
    crontab_text="${crontab_text}0 "
else
    crontab_text="${crontab_text}*/${timedelta_minutes} "
fi

if [[ $timedelta_hours -eq 0 || $timedelta_hours -eq 1 || $timedelta_hours == "0" || $timedelta_hours == "1" ]]; then
    crontab_text="${crontab_text}* "
else
    crontab_text="${crontab_text}*/${timedelta_hours} "
fi

crontab_text="${crontab_text}* * * cd ${current_directory} && ./updatetonerdata.sh"

echo "${crontab_text}" > $current_directory/crontab_updatetonerdata

# Activate crontab
crontab -u $username $current_directory/crontab_updatetonerdata


# Create Gunicorn socket file
gunicorn_socket_file_text=\
"[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
"

echo "${gunicorn_socket_file_text}" | sudo tee /etc/systemd/system/gunicorn.socket


# Create Gunicorn service file
gunicorn_service_file_text=\
"[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$username
Group=www-data
WorkingDirectory=$current_directory/Open_Printer_Management_System
ExecStart=$current_directory/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn.sock \\
          Open_Printer_Management_System.wsgi:application

[Install]
WantedBy=multi-user.target
"
echo "${gunicorn_service_file_text}" | sudo tee /etc/systemd/system/gunicorn.service

# Start and enable gunicorn socket
sudo systemctl start gunicorn.socket && sudo systemctl enable gunicorn.socket || sudo service gunicorn.socket start

# Activate gunicorn
curl --unix-socket /run/gunicorn.sock localhost

sudo systemctl daemon-reload && sudo systemctl restart gunicorn

# Get IP address for Nginx
ip_address=$(hostname -I)

# Create Nginx file
nginx_file_text=\
"server {
    listen 80;
    server_name 127.0.0.1 ${ip_address};
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $current_directory/Open_Printer_Management_System;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
"
echo "${nginx_file_text}" | sudo tee /etc/nginx/sites-available/Open-Printer-Management-System

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/Open-Printer-Management-System /etc/nginx/sites-enabled

# Change user for Nginx config
original_nginx_user_data="user www-data;"
new_nginx_user_data="user $username;"
sudo sed -i -e "s~${original_nginx_user_data}~${new_nginx_user_data}~g" /etc/nginx/nginx.conf

# Restart Nginx service
sudo systemctl restart nginx || sudo service nginx restart

# Install enable and allow firewall apps
sudo apt install ufw -y

if sudo ufw status | grep 'Status: inactive'; then
    echo "y" |sudo ufw enable
fi

sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH

echo -e "\n\n------------------------------------------------------------------------------------------\n"
while :; do
    read -p "Please enter the username for the admin account: " admin_username
    read -p "Please enter the password for the admin account: " admin_password
    read -p "Please enter the email address for the admin account: " admin_email

    export DJANGO_SUPERUSER_USERNAME=$admin_username
    export DJANGO_SUPERUSER_PASSWORD=$admin_password
    export DJANGO_SUPERUSER_EMAIL=$admin_email

    $current_directory/venv/bin/python $current_directory/Open_Printer_Management_System/manage.py createsuperuser --no-input

    if [[ $? == 0 ]]; then
        unset DJANGO_SUPERUSER_USERNAME
        unset DJANGO_SUPERUSER_PASSWORD
        unset DJANGO_SUPERUSER_EMAIL
        break
    fi
    echo ""
done

# Tell the user the installation has completed
echo -e "\n\n\n\n\n------------------------------------------------------------------------------------------\n"
echo -e "Installation complete!\n"
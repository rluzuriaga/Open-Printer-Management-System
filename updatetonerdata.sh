#!/bin/bash

seconds=0
cron_log_file=${PWD}/logs/updatetonerdata.log

if [[ ! -d "${PWD}/logs/" ]]; then
    mkdir "${PWD}/logs/"
fi

if [[ ! -f $cron_log_file ]]; then
    touch $cron_log_file
fi

echo "Starting" >> ${cron_log_file}
date >> ${cron_log_file}

source venv/bin/activate
cd Open_Printer_Management_System
python manage.py updatetonerdata >> ${cron_log_file} 2>&1

echo "Finished." >> ${cron_log_file}
duration=$seconds
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed.\n" >> ${cron_log_file}

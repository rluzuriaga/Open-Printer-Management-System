#!/usr/bin/env bash
SECONDS=0
PROJECT_PATH=/path/to/project/Open-Printer-Management-System
CRON_LOG_FILE=${PROJECT_PATH}/logs/updatetonerdata.log

echo "Starting" >> ${CRON_LOG_FILE}
date >> ${CRON_LOG_FILE}

cd ${PROJECT_PATH}
source venv/bin/activate
cd Open_Printer_Management_System
python manage.py updatetonerdata >> ${CRON_LOG_FILE} 2>&1

echo "Finished." >> ${CRON_LOG_FILE}
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed.\n" >> ${CRON_LOG_FILE}

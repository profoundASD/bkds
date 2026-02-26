"""
Usage: python3 bkdsJobScheduler.py $BKDS_AUTO_SCHED/bkds_locks $BKDS_AUTO_SCHED/scheduler_log $BKDS_AUTO_SCHED/task_log $BKDS_AUTO_SCHED_DATA/bkdsJobSchedule.json
Called from: bkdsAutomationLoop.sh registered as systemd
BKDS Job Scheduler

    This program serves as a versatile job scheduler, tailored to execute specific tasks at predetermined intervals, 
    with a focus on maintaining a minimum wait time between each task's executions.

"""
import datetime
import os
import zipfile
from pathlib import Path
from threading import Thread
import sys
import os
from bkdsLogMsg import log_msg

#export PYTHONPATH="$BKDS_UTIL_PYTHON"
#####################################################################
# Main Setup / Variables
#setup paths for lock/log files
bkds_locks = os.getenv("BKDS_AUTO_SCHED_LOCKS")
bkds_task = os.getenv("BKDS_UTIL_LOGS")
bkds_auto = os.getenv("BKDS_UTIL_LOGS")
output_file_prefix='bkds_auto_maint'
# Check if environment variables are set
if not bkds_locks or not bkds_task or not bkds_auto:
    print("Error: Necessary environment variables are not set.")
    sys.exit(1)

#archive detail
max_log_files=8
max_zip_files=8
#archive settings
archive_logs_older_than=5
archive_logs_older_than_unit='min'
purge_log_archives_older_than=7
purge_archives_older_unit='day'
########################################################################
#  Main logic and functions



def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_AUTO_SCHED', msg)


def purge_and_zip_old_files(directories, archive_logs_older_than, archive_logs_older_than_unit, purge_log_archives_older_than, purge_archives_older_unit, max_log_files, max_zip_files):
    logMsg(f"maintenance process beginning")

    time_units = {
        'min': 'minutes',
        'hour': 'hours',
        'sec': 'seconds',
        'day': 'days',
        'month': 'days'  
    }

    def get_time_delta(value, unit):
        if unit == 'month':
            return datetime.timedelta(**{time_units[unit]: value * 30})
        return datetime.timedelta(**{time_units[unit]: value})

    file_purge_delta = get_time_delta(archive_logs_older_than, archive_logs_older_than_unit)
    zip_purge_delta = get_time_delta(purge_log_archives_older_than, purge_archives_older_unit)

    now = datetime.datetime.now()
    logMsg(f"checking diectories @{now}")
    for dir_path in directories:
        #logMsg(f"checking directory: {dir_path}")
        # Get all non-zip files and sort by modification time
        all_log_files = sorted(Path(dir_path).glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
        # Limit the number of log files
        if len(all_log_files) > max_log_files:
            for file in all_log_files[max_log_files:]:
                os.remove(file)
                #logMsg(f"Removed excess log file: {file}")
       
        #get all files again after purging older
        all_log_files = sorted(Path(dir_path).glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
        # Find older files to zip
        files_to_zip = [f for f in all_log_files if now - datetime.datetime.fromtimestamp(f.stat().st_mtime) > file_purge_delta]
        # Zip files into a single zip file if there are any
        if files_to_zip:
            #logMsg(f"files to zip")
            zip_file_name = f"{dir_path}/{output_file_prefix}_archive_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
            with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files_to_zip:
                    zipf.write(file, arcname=file.name)
                    os.remove(file)
                    #logMsg(f"Zipped and current file: {file}")
        # Get all zip files and sort by modification time
        all_zip_files = sorted(Path(dir_path).glob('*.zip'), key=lambda x: x.stat().st_mtime, reverse=True)

        # Limit the number of zip files by both number and date
        if len(all_zip_files) > max_zip_files:
            for zip_file in all_zip_files[max_zip_files:]:
                os.remove(zip_file)
                #logMsg(f"Removed old zip file: {zip_file}")

        all_zip_files = sorted(Path(dir_path).glob('*.zip'), key=lambda x: x.stat().st_mtime, reverse=True)
        # Delete older zip files
        for zip_file in all_zip_files:
            if now - datetime.datetime.fromtimestamp(zip_file.stat().st_mtime) > zip_purge_delta:
                os.remove(zip_file)
                #logMsg(f"Deleted old zip file: {zip_file}")

if __name__ == "__main__":

    directories = [bkds_locks, bkds_task, bkds_auto]
    purge_and_zip_old_files(directories
                          , archive_logs_older_than
                          , archive_logs_older_than_unit
                          , purge_log_archives_older_than
                          , purge_archives_older_unit
                           ,max_log_files
                           ,max_zip_files)
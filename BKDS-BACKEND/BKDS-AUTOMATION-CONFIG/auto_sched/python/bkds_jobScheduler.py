import argparse
import datetime
import json
import os
import subprocess
import zipfile
import sys
import hashlib
import re
import socket
import time
from bkds_Utilities import log_msg

#####################################################################
#####################################################################
# Main Setup / Variables

# Set up argparse to handle command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='BKDS Job Scheduler')
    parser.add_argument('job_schedule_path', type=str, help='Path to the job schedule JSON file')
    parser.add_argument('--max_tasks', type=int, default=100, help='Maximum number of tasks to run (default: 10)')
    parser.add_argument('--interval_wait', type=int, default=10, help='Interval wait time between tasks (default: 10 seconds)')
    parser.add_argument('--interval_wait_units', type=str, default="seconds", help='Time units for the interval wait (default: seconds)')
    
    return parser.parse_args()

# Parse the arguments
args = parse_arguments()

job_schedule_path = args.job_schedule_path
task_counter = 0
max_tasks = args.max_tasks
interval_wait = args.interval_wait
interval_wait_units = args.interval_wait_units
# You can set interval_wait to 0 if needed
# interval_wait = 0
active_key = "active"
hostname = socket.gethostname()
program_name = os.path.basename(sys.argv[0])
output_file_prefix = 'bkds_auto'
bkds_util_python = os.environ.get("BKDS_UTIL_PYTHON")

# Expiration limits
LOCK_EXPIRATION_MINUTES = 30  # Lock file expiration in minutes
LASTRUN_EXPIRATION_DAYS = 1   # Last run file expiration in days
LAST_RUN_EXT = 'lastrun'

# Setup paths for lock/log files
bkds_auto_sched = os.getenv("BKDS_AUTO_SCHED_DATA")
bkds_locks = os.getenv("BKDS_AUTO_SCHED_LOCKS")
bkds_task = os.getenv("BKDS_UTIL_LOGS")

ORPHAN_TASK = "BKDS_ORPHAN_TASK"

# Directory for archives
archive_dir = os.path.join(bkds_locks, "archive")
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

#####################################################################
# Logging

def logMsg(msg):
    log_msg(program_name, "BKDS_JOB_SCHEDULER", msg)
    print(msg)

#####################################################################
# Utility Functions

def is_time_to_run(last_run_file, min_wait_min):
    if not os.path.exists(last_run_file):
        return True

    with open(last_run_file, 'r') as file:
        lines = file.readlines()

        if len(lines) >= 2:
            last_run_time_str = lines[1].strip()
        elif len(lines) == 1:
            last_run_time_str = lines[0].strip()
        else:
            return True

        last_run_time = datetime.datetime.fromisoformat(last_run_time_str)

    min_wait_seconds = float(min_wait_min) * 60
    min_wait_delta = datetime.timedelta(seconds=min_wait_seconds)

    return datetime.datetime.now() - last_run_time > min_wait_delta

def update_last_run_time(last_run_file, command):
    with open(last_run_file, 'w') as file:
        file.write(f'{command}\n{datetime.datetime.now().isoformat()}')

def generate_safe_name(command_list, batch_id):
    command_string = ' '.join(command_list)
    hasher = hashlib.sha256()
    hasher.update(command_string.encode('utf-8'))
    return f"{batch_id}_{hasher.hexdigest()[:10]}"

def expand_env_vars(arg, base_paths):
    def replace_with_env(match):
        key = match.group(1)
        val = base_paths.get(key, match.group(0))
        # Resolve any environment variables in val
        if val.startswith("$"):
            env_var = val[1:]
            val = os.environ.get(env_var, val)
        return val
    pattern = r'\{(\w+)\}'
    return re.sub(pattern, replace_with_env, arg)

#####################################################################
# Task Handling

def run_task(task, base_paths):
    lock_file = None
    command_list = None
    automation_id = task.get('automation_id', ORPHAN_TASK)
    try:
        script_path = expand_env_vars(task['script_path'], base_paths)
        interpreter = task['interpreter']
        # Construct the arguments list with proper expansion and quoting
        args = [expand_env_vars(task['arguments'].get(f"arg_{i+1}", ""), base_paths) for i in range(len(task['arguments']))]
        command_list = [interpreter, script_path] + args

        # Generate safe name and file paths
        safe_name = generate_safe_name(command_list, automation_id)
        lock_file = os.path.join(bkds_locks, f"{safe_name}.lock")
        last_run_file = os.path.join(bkds_locks, f"{safe_name}.{LAST_RUN_EXT}")

        # Check if the task can run
        if os.path.exists(lock_file):
            logMsg(f"Lock file exists for task (Automation ID: {automation_id}), skipping execution.")
            return
        if not is_time_to_run(last_run_file, task['min_wait_min']):
            logMsg(f"Minimum wait time not met for task (Automation ID: {automation_id}), skipping execution.")
            return

        # Execute the task
        try:
            with open(lock_file, 'w') as f_lock:
                f_lock.write(f"Task locked for Automation ID: {automation_id}\nCommand: {command_list}\n")

            logMsg(f"Executing task (Automation ID: {automation_id}): {command_list}")
            # Execute the command list directly without joining into a string
            subprocess.run(command_list, check=True)

            update_last_run_time(last_run_file, ' '.join(command_list))
            logMsg(f"Task completed successfully (Automation ID: {automation_id}): {' '.join(command_list)}")
        except subprocess.CalledProcessError as e:
            logMsg(f"Task execution failed (Automation ID: {automation_id}): {' '.join(command_list)} with error: {e}")
        except Exception as e:
            logMsg(f"Unexpected error during task execution (Automation ID: {automation_id}): {' '.join(command_list)} with error: {e}")
    finally:
        if lock_file and os.path.exists(lock_file):
            os.remove(lock_file)
            logMsg(f"Lock file removed for task (Automation ID: {automation_id})")
            
#####################################################################
# Main Execution

if __name__ == "__main__":
    logMsg(f"Job Schedule Path: {job_schedule_path}")
    logMsg(f"Max Tasks: {max_tasks}")
    logMsg(f"Interval Wait: {interval_wait} {interval_wait_units}")

    if len(sys.argv) < 2:
        logMsg("Usage: python script.py <schedule_json>")
        sys.exit(1)

    # After loading the JSON configuration
    with open(job_schedule_path) as file:
        config = json.load(file)

    # Resolve environment variables in base_paths
    base_paths = config["base_paths"]
    resolved_base_paths = {}
    for key, value in base_paths.items():
        if value.startswith("$"):
            env_var = value[1:]
            resolved_value = os.environ.get(env_var, value)
            resolved_base_paths[key] = resolved_value
        else:
            resolved_base_paths[key] = value
    base_paths = resolved_base_paths
    tasks = config["tasks"]

    # Process each task
    for task in tasks:
        if task.get("schedule") == active_key:
            logMsg(f"Running task: {task['name']}")
            try:
                run_task(task, base_paths)
            except Exception as e:
                logMsg(f"Error executing task {task['name']}: {e}")
            task_counter += 1
            if task_counter >= max_tasks:
                break
            time.sleep(interval_wait)  # You can adjust interval_wait as needed
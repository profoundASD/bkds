#!/bin/bash
################################
#
# Script: BKDS Automated Execution Script
#
# This script handles the sequential execution of three backend processes:
# - bkds_backend_contentGen_GetRocketLaunchData.py
# - bkds_contentGen_RocketLaunchPostGen.py
# - bkds_backend_yt_channelGet.py
#
# Each script maintains its own execution constraint via a `.lastrun` file.
# The script will check the last execution time and skip execution if
# the minimum wait time has not elapsed.
#
################################

# Ensure at least one argument is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <batch_id>"
    exit 1
fi

#####################################################################
# Setup and Configuration
#####################################################################

# Command-line arguments
batch_id=$1

# Program and environment setup
program_name="$(basename "${0%.*}")"

# Environment variables
LOCK_DIR="${BKDS_AUTO_SCHED_LOCKS:-/tmp/bkds_locks}"
PYTHON_PATH="${BKDS_UTIL_PYTHON:-/usr/local/bin/python_scripts}"
LOG_SCRIPT="$PYTHON_PATH/bkds_LogMsg.py"
MIN_WAIT_TIME=5
ROCKET_LAUNCH_API_WAIT=2700
ROCKET_LAUNCH_POST_WAIT=1800
YT_ROCKET_LAUNCH_GET_VIDEO_WAIT=14400

# Script-specific minimum wait times (in seconds)
declare -A SCRIPT_WAIT_TIMES=(
    ["bkds_backend_contentGen_GetRocketLaunchData.py"]=$ROCKET_LAUNCH_API_WAIT  # 45 minutes
    ["bkds_backend_contentGen_GenRocketLaunchPost.py"]=$ROCKET_LAUNCH_POST_WAIT  # 30 minutes
    ["bkds_backend_yt_channelGet.py"]=$YT_ROCKET_LAUNCH_GET_VIDEO_WAIT           # 4 hours
)

# List of scripts to execute
SCRIPTS=(
    "bkds_backend_contentGen_GetRocketLaunchData.py"
    "bkds_backend_yt_channelGet.py"
    "bkds_backend_contentGen_GenRocketLaunchPost.py"
)

# Logging function
log_msg() {
    local message="$1"
    echo "[$(date)] $message"
    python3 "$LOG_SCRIPT" "$program_name" "$batch_id" "$message"
}

#####################################################################
# Functions
#####################################################################

# Function to generate the path for a .lastrun file
get_lastrun_file() {
    local script_path="$1"
    local hash=$(md5sum "$script_path" | awk '{print $1}')
    echo "$LOCK_DIR/$(basename "$script_path" .py)_$hash.lastrun"
}

# Function to check if a script can run based on its last execution time
can_run_script() {
    local script_path="$1"
    local wait_time="$2"
    local lastrun_file
    lastrun_file=$(get_lastrun_file "$script_path")

    # Skip wait time check if wait_time is 0
    if ((wait_time == 0)); then
        log_msg "$script has no wait time constraint. Executing unconditionally."
        return 0
    fi

    # Check if the .lastrun file exists
    if [[ -f "$lastrun_file" ]]; then
        local last_run_time
        last_run_time=$(tail -n 1 "$lastrun_file")
        local last_run_time_clean
        last_run_time_clean=$(echo "$last_run_time" | cut -d '.' -f 1)
        local last_run_epoch
        last_run_epoch=$(date -d "$last_run_time_clean" +%s 2>/dev/null)

        if [[ $? -ne 0 ]]; then
            log_msg "Failed to parse last run time: $last_run_time."
            return 0
        fi

        local current_epoch
        current_epoch=$(date +%s)
        local elapsed_time=$((current_epoch - last_run_epoch))

        if ((elapsed_time < wait_time)); then
            log_msg "Skipping $script_path: Last run was $elapsed_time seconds ago (Minimum: $wait_time seconds)."
            return 1
        fi
    else
        log_msg ".lastrun file not found for $script_path. Proceeding as first run."
    fi
    return 0
}


# Function to record the last run time for a script
write_lastrun_file() {
    local script_path="$1"
    local lastrun_file
    lastrun_file=$(get_lastrun_file "$script_path")
    local timestamp
    timestamp=$(date +"%Y-%m-%dT%H:%M:%S.%6N")
    echo "['python3', '$script_path']" > "$lastrun_file"
    echo "$timestamp" >> "$lastrun_file"
    log_msg "Updated .lastrun file: $lastrun_file"
}

#####################################################################
# Main Execution
#####################################################################

# Ensure LOCK_DIR exists
mkdir -p "$LOCK_DIR"

log_msg "Starting BKDS execution cycle."

for script in "${SCRIPTS[@]}"; do
    script_path="$PYTHON_PATH/$script"
    wait_time="${SCRIPT_WAIT_TIMES[$script]:-300}"  # Default to 5 minutes if not specified

    if [[ -f "$script_path" ]]; then
        # Check if the script can run
        if can_run_script "$script_path" "$wait_time"; then
            log_msg "Executing script: $script with batch_id: $batch_id"
            python3 "$script_path" "$batch_id"

            if [[ $? -eq 0 ]]; then
                log_msg "Execution of $script succeeded."
                write_lastrun_file "$script_path"
            else
                log_msg "Execution of $script failed."
                exit 1
            fi
        fi
    else
        log_msg "Script not found: $script_path"
        exit 1
    fi

    # Wait before proceeding to the next script
    log_msg "Waiting for $MIN_WAIT_TIME seconds before checking the next script."
    sleep "$MIN_WAIT_TIME"
done

log_msg "Completed BKDS execution cycle."

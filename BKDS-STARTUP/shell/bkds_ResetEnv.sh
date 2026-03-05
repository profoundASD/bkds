#!/bin/bash
#####################################################################
# Usage:
# Description:
#####################################################################
# Main Setup / Variables
program_name=$(basename "$0")
batch_id=$1
#shell scripts used
log_script=$BKDS_UTIL_PYTHON/bkds_LogMsg.py

########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

# Log the start of the script
log_msg "Starting environment reset script..."

# Loop through each argument passed to the script
for app in "${@:2}"; do # Start from the second argument
    killall -9 "$app"
done

log_msg "Killed relevant processes."

sleep 0.05

# Call the reposition script and log
#bash $shell_path/shiftXDO.sh $batch_id key Super+Home
#log_msg "Repositioned windows."

# Log the completion of the script
log_msg "Environment reset script completed."
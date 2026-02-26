#!/bin/bash
#####################################################################
# Usage: ./start_nodemon_and_chrome.sh
# Description:
#   This script checks if Nodemon is running, starts it if necessary,
#   and then launches Google Chrome to access localhost on port 3000.
#
# Behavior:
#   - Verifies if Nodemon is running.
#   - Starts Nodemon using a pre-defined script if not running.
#   - Launches Chrome via Flatpak after ensuring Nodemon is active.
#####################################################################

# Main Setup / Variables
program_name=$(basename "$0")
batch_id='BKDS_NODEJS_APP'
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
nodemon_check_cmd="pgrep -x nodemon"
start_nodemon_script="$BKDS_UTIL_SHELL/bkds_nodemon_start.sh"
chrome_command="flatpak run com.google.Chrome http://localhost:3000"

# Function for logging
log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

# Check if Nodemon is running
log_msg "Checking if Nodemon is running..."
if $nodemon_check_cmd > /dev/null; then
    log_msg "Nodemon is already running."
else
    log_msg "Nodemon is not running. Starting Nodemon in the background..."
    if bash "$start_nodemon_script" & then
        log_msg "Successfully started Nodemon using: $start_nodemon_script"
        sleep 2  # Give Nodemon a moment to initialize
    else
        log_msg "Failed to start Nodemon using: $start_nodemon_script"
        exit 1
    fi
fi

# Launch Chrome
log_msg "Launching Chrome to access http://localhost:3000..."
killall -9 chrome || log_msg "No existing Chrome processes to kill."
$chrome_command &  # Run Chrome in the background
if [ $? -eq 0 ]; then
    log_msg "Chrome launched successfully with: $chrome_command"
else
    log_msg "Failed to launch Chrome with: $chrome_command"
    exit 1
fi


# Log the completion of the script
log_msg "Script execution completed."

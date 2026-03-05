#!/bin/bash
########################################################################
# Custom Shell Script
# Purpose: Check for Netdata service and start it if not running
#
# Usage: bash $SCRIPT_PATH/startNetdata.sh
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
node_id=$2
# Python scripts used for logging (assuming similar setup as your script)
log_script=$UTIL_PYTHON_PATH/bkds_LogMsg.py

# Apps launched
app="netdata"

########################################################################
# Main logic and functions

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

# Function to start Netdata
start_netdata() {
    sudo systemctl start $app
}

# Check if Netdata is installed
if ! command -v $app &> /dev/null; then
    log_msg "$app is not installed. Please install $app"
    exit 1
fi

# Check if Netdata is running
if ! pgrep -x "$app" > /dev/null; then
    # Start Netdata if not running
    log_msg "Starting $app"
    start_netdata &
    log_msg "$app launch attempted"
    # Loop for up to 10 seconds to check if Netdata starts
    for i in {1..10}; do
        log_msg "Checking for $app"
        if pgrep -x "$app" > /dev/null; then
            log_msg "$app is now running"
            break
        fi
        sleep 1
    done

    if ! pgrep -x "$app" > /dev/null; then
        log_msg "Failed to start $app after 10 seconds"
    fi
else
    # Log that Netdata is already running
    log_msg "$app is already running"
fi
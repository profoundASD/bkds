#!/bin/bash
#####################################################################
# Usage: ./start_redshift.sh [batch_id]
# Description: 
#   This script launches or terminates Redshift based on the current time.
#   It activates Redshift within a predefined night mode window and 
#   logs actions to a specified Python logger script.
# 
# Arguments:
#   batch_id: (Optional) An identifier for the batch process used in logging.
# 
# Example:
#   ./start_redshift.sh 1234
# 
# Behavior:
#   - Redshift starts with specific location and color temperature settings.
#   - Redshift runs in night mode between 4:30 PM and 9:00 AM.
#   - If Redshift is already running within the window, no action is taken.
#   - Outside the night mode window, Redshift is terminated if running.
#####################################################################

# Main Setup / Variables
program_name=$(basename "$0")
batch_id='BKDS_REDSHIFT_APP'
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"

# Redshift configuration
start_hour=16  # 4:30 PM
start_minute=30
end_hour=9     # 9:00 AM
end_minute=0
redshift_day=6500    # Day temperature (6500K)
redshift_night=3000  # Night temperature (3000K)
redshift_lat=38.6270
redshift_long=-90.1994
window_util='randr'  # RandR utility for adjusting screen

# Function for logging
log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

# Log the start of the script
log_msg "Starting Redshift launch script..."

# Get the current time in hours and minutes (24-hour format)
current_hour=$(date +"%H")
current_minute=$(date +"%M")

# Construct the Redshift command
redshift_cmd="redshift -l $redshift_lat:$redshift_long -m $window_util -t $redshift_day:$redshift_night &"

# Check if the current time is within the night mode window
is_within_night_mode=false
if (( current_hour > start_hour || (current_hour == start_hour && current_minute >= start_minute) )); then
    is_within_night_mode=true
elif (( current_hour < end_hour || (current_hour == end_hour && current_minute < end_minute) )); then
    is_within_night_mode=true
fi

# Check if Redshift is already running
is_redshift_running=$(pgrep -x redshift > /dev/null && echo true || echo false)

# If within night mode window, ensure Redshift is running
if $is_within_night_mode; then
    if $is_redshift_running; then
        log_msg "Redshift is already running within the night mode window. No action required."
    else
        # Start Redshift
        eval "$redshift_cmd"
        log_msg "Launched Redshift in night mode."
    fi
# If outside the night mode window, terminate Redshift if running
else
    if $is_redshift_running; then
        pkill -SIGTERM redshift
        log_msg "Terminated Redshift as it's outside the night mode window."
    else
        log_msg "Redshift is not running, and it's outside the night mode window. No action required."
    fi
fi

# Log the completion of the script
log_msg "Redshift launch script completed."

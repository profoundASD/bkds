#!/bin/bash
########################################################################
# BKDS 
# Purpose: launch conky app for desktop visualization of settings to user
#
#
# Usage: bash $BKDS_STARTUP_SHELL/bkdsConkyLaunch.sh BKDSTESTPC00
#####################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
node_id='bkds-desktop-large'
#node_id='bkds-laptop-small'

# Python scripts used
log_script=$BKDS_UTIL_PYTHON/bkds_LogMsg.py
# Path to Conky profile
conky_profile1="$BKDS_DESKTOP_DATA/$node_id-conky-profile.txt" 
conky_profile2="$BKDS_DESKTOP_DATA/$node_id-conky-time-insight.txt" 

# Apps launched
app="conky"
app_options1="-c $conky_profile1"
app_options2="-c $conky_profile2"
#app_options3="-c $conky_profile3"
########################################################################
# Main logic and functions

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

restart_conky() {
    profile=$1
    options=$2
    
    # Check if Conky with the given profile is already running
    if pgrep -fx "$app $options" > /dev/null; then
        # Terminate running Conky with the specified profile
        pkill -fx "$app $options"
        log_msg "Terminated running Conky process with profile $profile"
    fi

    # Start Conky with the given profile
    $app $options &
    log_msg "$app launched with profile $profile \\n command: $app $options"
}

# Restart Conky with profile 1
restart_conky "$conky_profile1" "$app_options1"

# Restart Conky with profile 2
restart_conky "$conky_profile2" "$app_options2"

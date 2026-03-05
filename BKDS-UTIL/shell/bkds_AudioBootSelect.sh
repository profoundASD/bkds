#!/bin/bash
########################################################################
# BKDS 
# Purpose: set volume settings on boot
########################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1

# Environment variables
python="python3"

#shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"

keywords=("Unitek") # Keywords to blacklist
$app1="audio boot select"

$cmd1="pacmd list-sinks"
$cmd2="pacmd set-default-sink"
########################################################################
#  Main logic and functions

log_msg() {
    $python $log_script "$program_name" "$batch_id" "$1" && echo "$1"
} 

#keywords=("Unitek" "Microphone" "HDMI")
log_msg "$app1 start for $batch_id and $program_name"

# Get a list of audio output devices
devices=$($cmd1 | grep -E -i "name:|description:" | grep -i -E "${keywords[0]}" | grep -i -E "${keywords[1]}" | grep -i -E "${keywords[2]}" | grep -v -i -E "${keywords[@]}" | awk '/index:/{print $2}')

# Loop through each device and check if it matches a keyword
while read -r line; do
    if echo "$line" | grep -q -i "${keywords[@]}"; then
        # If a keyword is found, set the device as blacklisted
        $cmd2 $(echo "$line" | awk -F': ' '{print $2}')
    fi
done <<< "$devices"

log_msg "$app1 done for $batch_id and $program_name"
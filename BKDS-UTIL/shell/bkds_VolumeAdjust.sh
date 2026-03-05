#!/bin/bash
########################################################################
# BKDS Volume Adjustment Script
# 
# Purpose:
# This script logs actions, retrieves the current default sink volume,
# and launches a Python program to adjust volume.
#
# Features:
# - Logs script actions using a Python logging utility.
# - Dynamically retrieves the default sink's current volume.
# - Calls a Python program with the duration and current volume as arguments.
#
# Usage:
# ./bkdsVolumeAdjust.sh <batch_id>
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
volume=$2



# Python scripts used
python_path="$BKDS_UTIL_PYTHON"
adjust_volume_script="$python_path/bkdsVolumeAdjust.py"
log_script="$python_path/bkds_LogMsg.py"
audio_path="/usr/share/sounds/freedesktop/stereo"
audio_effect='audio-volume-change.oga'
audio_updated_effect="bkdsSoundUpdated.mp3"
audio_file=$audio_path/$audio_effect
audio_file2="$BKDS_UTIL_MP3/$audio_updated_effect"

audio_app="/usr/bin/paplay"
# Hardcoded duration
DURATION=8

########################################################################
# Functions

log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

get_default_sink_volume() {
    # Get the default sink name
    local default_sink
    default_sink=$(pactl info | grep 'Default Sink' | awk '{print $3}')
    
    if [ -z "$default_sink" ]; then
        echo "Error: Default sink not found." >&2
        return 1
    fi

    # Get the current volume for the default sink
    #local volume
    #volume=$(pactl list sinks | grep -A 15 "$default_sink" | grep -oP '\d+%' | head -1 | sed 's/%//')

    if [ -z "$volume" ]; then
        echo "Error: Could not retrieve volume for sink $default_sink." >&2
        return 1
    fi

    echo "$volume"
}

########################################################################
# Main Logic

# Validate input
if [ -z "$batch_id" ]; then
    log_msg "Usage: $program_name <batch_id>"
    exit 1
fi

# Retrieve the current volume of the default sink
CURRENT_VOLUME=$(get_default_sink_volume)
if [ -z "$CURRENT_VOLUME" ]; then
    log_msg "Failed to retrieve current volume. Exiting."
    exit 1
fi

# Log start
log_msg "Launching Python script with duration=$DURATION and volume=$CURRENT_VOLUME"

# Play audio feedback
$audio_app "$audio_file"
sleep 0.25
$audio_app "$audio_file"
sleep 0.25
#$audio_app "$audio_file2" &
#sleep 1.5
# Call the Python program with duration and current volume
python3 "$adjust_volume_script" "$DURATION" "$CURRENT_VOLUME" &



# Log completion
log_msg "Script completed successfully."
log_msg "Done setting audio volume to $CURRENT_VOLUME% and playing $audio_file"
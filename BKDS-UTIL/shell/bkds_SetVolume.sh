#!/bin/bash
########################################################################
# BKDS 
# Purpose: Set volume settings using pactl and PulseAudio
########################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1

# Environment variables
python="python3"

# Shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
# Audio files used
audio_vol=$2
########################################################################
# Main logic and functions

log_msg() {
    $python $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "Setting audio volume to $audio_vol% and playing $audio_file"

# Unmute and set the volume using pactl
pactl set-sink-mute @DEFAULT_SINK@ 0
sleep 1
pactl set-sink-volume @DEFAULT_SINK@ "$audio_vol%"

sleep 1


log_msg "Done setting audio volume to $audio_vol%"
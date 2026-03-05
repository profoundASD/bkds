#!/bin/bash
#####################################################################
# Usage:
# Description:
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id="$1"


########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "program_name: $program_name"
log_msg "base_name: $0"
log_msg "batch id: $batch_id"

xdotool key Super
sleep 0.05
xdotool key Super

xdotool key Super
sleep 0.05
xdotool key Super
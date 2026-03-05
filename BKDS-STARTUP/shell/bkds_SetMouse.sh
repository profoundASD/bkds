#!/bin/bash
########################################################################
# BKDS Mouse Button Remapper
# This script remaps the right-click button on all connected mice to act as left-click.
# It dynamically detects all connected pointer devices and applies the remapping.
#
# Usage:
#   ./mouseRemap.sh [BatchID]
########################################################################
# Main Setup / Variables

# Set base variables
program_name="$(basename "${0%.*}")"
batch_id="${1}_SETMOUSE"

# Python script for logging
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"

# Wait time for desktop environment to initialize
wait_time=2
shell_script="$BKDS_UTIL_SHELL/bkds_mouseSettings.sh"

########################################################################
#  Main logic and functions

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "Starting mouse button remapping..."

# Wait for the desktop environment to fully load
log_msg "Waiting for $wait_time seconds to ensure desktop environment is initialized."
sleep $wait_time

bash $shell_script $batch_id

log_msg "Mouse button remapping completed successfully."

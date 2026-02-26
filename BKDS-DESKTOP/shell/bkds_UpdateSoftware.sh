#!/bin/bash

########################################################################
# BKDS Software Updater Script
#
# This script provides a user-friendly interface for managing software
# updates on Xubuntu. It plays audio notifications, displays an
# informative dialog box (if a display is available), and launches the
# Xubuntu software updater. It also includes rate limiting to prevent
# excessive update checks, ensuring system stability and a smooth user
# experience.
#
# Shared functions are sourced from bkds_CommonFunctions.sh.
#
########################################################################

# Source the common functions
: "${BKDS_UTIL_SHELL:?BKDS_UTIL_SHELL not set}"
source "$BKDS_UTIL_SHELL/bkds_desktop_CommonFunctions.sh"

# --- Main Setup / Variables ---
program_name="$(basename "${0%.*}")"
batch_id="${1:-$program_name}"
script_hash=$(tr -d '\r\t' < "$0" | tr -d '[:blank:]' | tr '[:upper:]' '[:lower:]' | md5sum | awk '{print $1}')

# Shell scripts used
audio_gen_script="$BKDS_UTIL_SHELL/bkds_AudioGen.sh" # Audio generation script

# Other files/settings used
audio_file="$BKDS_UTIL_MP3/bkdsSoftwareUpdate.mp3"
wake_mp3="$BKDS_UTIL_MP3/bkdsStartupSound.mp3"
audio_app="mpg123"
update_app="update-manager"
rate_limit_file="$BKDS_UTIL_DATA/config/bkds_rate_limit_software_update.json"  # JSON file for rate limiting
lastrun_file="$BKDS_AUTO_SCHED_LOCKS/${program_name}_${script_hash}.lastrun"
ui_message_base="The computer is up to date.  Please wait to check for updates until after:"
ui_message_trailer=" at the earliest"
ui_zenity_title="Special Delivery Message"
audio_gen_file_prefix="bkds_ui_audio_gen_softwareUpdate"
ui_zenity_timeout=18
lockout_limit_sec=15

# Default Rate Limit Values if not in config
default_daily_limit=1
default_weekly_limit=3
default_weekly_days=6

# --- Main Script Execution ---

# Acquire execution lock
acquire_execution_lock "$program_name" "$script_hash" "$lockout_limit_sec"

# Log start
log_msg "$program_name" "$batch_id" "Software Updater dialogue started"

# Check rate limits and exit if necessary.
check_rate_limit "$program_name" "$rate_limit_file" "$lastrun_file" "$default_daily_limit" "$default_weekly_limit" "$default_weekly_days" \
    "$ui_message_base" "$ui_message_trailer" "$ui_zenity_title" "$ui_zenity_timeout" "$audio_gen_file_prefix"

#Play audio and start the updater
log_msg "$program_name" "$batch_id" "Checking for existing processes"
if pgrep -x "$audio_app" > /dev/null; then
    log_msg "$program_name" "$batch_id" "Terminating existing $audio_app and $update_app processes"
    pkill -x "$update_app" 2> /dev/null
    pkill -x "$audio_app" 2> /dev/null
fi

# Play audio files using play_audio function
log_msg "$program_name" "$batch_id" "Playing audio notification: $audio_file"
play_audio "$audio_app" "$audio_file"

log_msg "$program_name" "$batch_id" "Playing audio notification: $wake_mp3"
play_audio "$audio_app" "$wake_mp3"

# Open update-manager in background
log_msg "$program_name" "$batch_id" "Opening $update_app"
"$update_app" &

log_msg "$program_name" "$batch_id" "Software Updater dialogue ended"

# Release execution lock
release_execution_lock "$program_name"

# Exit with success code
exit 0
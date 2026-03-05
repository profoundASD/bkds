#!/bin/bash

########################################################################
# BKDS System Control Script
#
# This script manages system states such as restart, shutdown, and sleep.
# It sends a UI message to an endpoint and pipes terminal messages back
# to the UI while executing the system command.
# It also implements rate limiting to prevent excessive restarts.
#
# Usage:
# ./script_name.sh [restart|shutdown|sleep]
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
power_center_selection="$2"
lockout_limit_sec=15
script_hash=$(md5sum "$0" | awk '{print $1}')

# Paths
audio_gen_script="$BKDS_UTIL_SHELL/bkds_AudioGen.sh"
audio_app_name='mpg123'
audio_app="/usr/bin/$audio_app_name"
restart_rate_limit_file="$BKDS_UTIL_DATA/config/bkds_rate_limit_restart_update.json"
restart_lastrun_file="$BKDS_AUTO_SCHED_LOCKS/${program_name}_${script_hash}.lastrun"

ui_message_base="The computer is ready for use and does not need to be restarted again until after: "
ui_message_trailer=" at the earliest"
ui_zenity_title="Special Delivery Message"
ui_zenity_timeout=18

audio_gen_file_prefix="bkds_ui_audio_gen_restartRateLimit"

# Commands
restart_command="reboot"
shutdown_command="shutdown now"
suspend_command="systemctl suspend"

# Audio Files
sleep_mp3="$BKDS_UTIL_MP3/bkdsSleeping.mp3"
restart_mp3="$BKDS_UTIL_MP3/bkdsRestarting.mp3"
shutdown_mp3="$BKDS_UTIL_MP3/bkdsShuttingDown.mp3"

# Default Rate Limit Values
default_daily_limit=1
default_weekly_limit=4
default_weekly_days=7

reboot_key="POWER_REBOOT"
shutdown_key="POWER_SHUTDOWN"
suspend_key="POWER_SLEEP"

# --- Main Logic ---

# Acquire execution lock
acquire_execution_lock "$program_name" "$script_hash" "$lockout_limit_sec"

# Check for valid power selection
case "$power_center_selection" in
    $reboot_key|$shutdown_key|$suspend_key)
        # Valid selection, continue
        ;;
    *)
        log_msg "$program_name" "$batch_id" "Invalid command: $power_center_selection"
        release_execution_lock "$program_name"
        exit 1
        ;;
esac

# Check restart rate limit if reboot is selected
if [[ "$power_center_selection" == "$reboot_key" ]]; then
    check_rate_limit "$program_name" "$restart_rate_limit_file" "$restart_lastrun_file" "$default_daily_limit" "$default_weekly_limit" "$default_weekly_days" \
        "$ui_message_base" "$ui_message_trailer" "$ui_zenity_title" "$ui_zenity_timeout" "$audio_gen_file_prefix"
fi
play_audio "$audio_app" "$audio_file"
# Set command and audio file based on selection
case "$power_center_selection" in
    $reboot_key)
        command_option="$restart_command"
        audio_file="$restart_mp3"
        ;;
    $shutdown_key)
        command_option="$shutdown_command"
        audio_file="$shutdown_mp3"
        ;;
    $suspend_key)
        command_option="$suspend_command"
        audio_file="$sleep_mp3"
        ;;
esac

# Execute command and play audio
log_msg "$program_name" "$batch_id" "Executing: $command_option"

sleep 2
$command_option
log_msg "$program_name" "$batch_id" "Command completed: $command_option"

# Release execution lock
release_execution_lock "$program_name"

# Exit with success code
exit 0
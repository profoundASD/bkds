#!/bin/bash
########################################################################
# BKDS System Update and Reboot Management Script
# This script manages system updates and reboots for BKDS systems. It checks for 
# update requirements and prompts users for a system reboot with audio notifications.
# The script handles user-initiated or scheduled update checks, ensures single 
# instance execution through lock files, and supports user interactions via Zenity.
# Audio cues provide an accessible interface, and shutdown commands are executed 
# based on user response or after a set number of ignored prompts.
#
#
# Usage: bash bkdsUpdateUbuntu.sh BKDS_UPDATE_UBUNTU DESKTOP #interactive from desktop
#        bash bkdsUpdateUbuntu.sh BKDS_UPDATE_UBUNTU AUTO_SCHED #automation
########################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
update_check_type=$2 #DESKTOP for user initiated or AUTO_SCHED for automation initiated
#shell path and scripts used
restart_notify_script="$BKDS_UTIL_SHELL/bkdsRestartNotify.sh $batch_id"
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
#audio files used
audio_file_update_check="$UTIL_MP3/bkds_spoken_update_check.mp3"
audio_file_uprade_check="$UTIL_MP3/bkds_spoken_upgrade_check.mp3"
audio_file_update_done="$UTIL_MP3/bkds_spoken_update_done.mp3"
audio_file_upgrade_done="$UTIL_MP3/bkds_spoken_upgrade_done.mp3"
#other settings/files used
audio_app="mpg123"
audio_app_options="-q"
#audio plays for interactive but is suppressed for automation
update_interactive=False
if echo "$update_check_type" | tr '[:upper:]' '[:lower:]' | grep -q "desktop"; then
    update_interactive=True
else
    update_interactive=False
fi
########################################################################
#  Main logic and functions

log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

# Function to play audio file
play_audio() {
    local audio_file=$1
    if [ "$update_interactive" = "True" ]; then
        log_msg "Desktop initiated"
        $audio_app "$audio_app_options" "$audio_file"
    else
        log_msg "Automation initiated"
        return
    fi
}

#updatee section
play_audio "$audio_file_update_check"
log_msg "Checking for update"
update_output=$(apt-get update -qq 2>&1)
log_msg "$update_output"
play_audio "$audio_file_update_done"
sleep 1
#upgrade section
play_audio "$audio_file_upgrade_check"
log_msg "Checking for upgrades"
upgrade_output=$(apt-get upgrade -qqy 2>&1)
log_msg "$upgrade_output"
play_audio "$audio_file_upgrade_complete"

#check reboot status/notify appropriately
log_msg "Checking for reboot status"
bash $restart_notify_script $batch_id

log_msg "done with update check"
#!/bin/bash
########################################################################
# System Reboot Management Script
# This script facilitates a controlled system reboot process following system updates. 
# It repeatedly checks for reboot necessity, prompts the user interactively if required, 
# and handles user responses for a manual or automatic system reboot. The script 
# incorporates audio notifications for user prompts and utilizes lock files to ensure 
# single-instance execution, enhancing usability and system safety.
#
#
# Usage: bash bkdsRestartNotify.sh BKDS_REBOOT_NOTIFY
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1

# Shell script and main files used
python_path="$BKDS_UTIL_PYTHON"
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
restart_ui_script="$BKDS_DESKTOP_SHELL/bkds_PowerControls.sh"
lock_path="$BKDS_UTIL_LOCKS"

#audio files used
audio_file_restarting_now="$UTIL_MP3/bkds_spoken_restarting_now.mp3"
audio_file_update_done="$UTIL_MP3/bkds_spoken_complete.mp3"

# Prompt settings
reminder_attempts=3
prompt_wait_time=10
prompt_timeout=20
prompt_window_title="Reboot Required"
prompt_text="System update completed. A reboot is required to apply changes. Do you want to restart now?"
prompt_restart_now="Restart Now"
prompt_ignore="Later"

#other files/settings used
reboot_check_attempts="4"
trigger_check_wait_time="3"
shutdown_commmand="shutdown -r now"
reboot_choice_msg="Rebooting after user choice."
reboot_ignored_msg="Forced reboot after multiple ignored update prompts."
lock_file="${lock_path}/${program_name}.lock"
reboot_trigger="/var/run/reboot-required"
restart_key="POWER_REBOOT"
########################################################################
#  Main logic and functions

log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo $1
}

play_audio() {
    local audio_file=$1
    if [ -f "$audio_file" ]; then
        mpg123 -q "$audio_file" &  # Play in background
    fi
}

# Functions for lock management
check_set_lock() {
    if [ -e "$lock_file" ]; then
        log_msg "Lock file exists. Exiting to prevent concurrent execution."
        exit 1
    else
        log_msg "Creating lock file"
        touch "$lock_file"
    fi
}
remove_lock() {
    rm -f "$lock_file"
}
# Set lock file and trap for clean exit
check_set_lock
trap 'remove_lock' EXIT

# Function to show a Zenity question dialog with a timeout and a Restart button
prompt_for_restart() {
    play_audio "$audio_file_restart_required"
    log_msg "launching zenity"
    zenity --question --text="$prompt_text" \
           --title="$prompt_window_title" \
           --ok-label="$prompt_ignore" \
           --cancel-label="$prompt_restart_now" \
           --timeout=$prompt_timeout
    log_msg "zenity prompt launched"
    return $?
}

# Main logic
#make a few attempts to check for reboot trigger and exit if not found
log_msg "Notification loop for $program_name and $batch_id starting"
for (( j=0; j < $reboot_check_attempts; j++ )); do    
    if [ -f "$reboot_trigger" ]; then
        log_msg "Reboot required, starting prompt loop"
        for (( i=0; i < reminder_attempts; i++ )); do
            prompt_for_restart
            if [ $? -eq 0 ]; then
                log_msg "User chose to restart now"
                break  # Exit the loop on user action
            else
                log_msg "giving user more time"
                sleep $prompt_wait_time
                log_msg "continuing prompt loop"
            fi
        done
        
        log_msg "Rebooting after $i attempts"
        play_audio "$audio_file_update_done"
        sleep 1
        play_audio "$audio_file_restarting_now"

        bash $restart_ui_script $batch_id $restart_key
        break  # Ensure to exit the outer loop after handling reboot
    fi

    sleep $trigger_check_wait_time
    log_msg "Re-checking reboot-required"
done
# Clean exit
exit 0

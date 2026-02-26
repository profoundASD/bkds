#!/bin/bash
########################################################################
# BKDS Chrome Termination Script
# Gracefully terminates Chrome sessions for a kiosk application.
#####################################################################
source /home/jason/.bashrc
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id="$1"
# Shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
# Other files/settings used
audio_app="/usr/bin/mpg123"
audio_path="$BKDS_UTIL_MP3"
desktop_mp3="$audio_path/bkdsShowingDesktop.mp3"
wake_mp3="$audio_path/bkdsStartupSound.mp3"

app="chrome"
timeout_seconds=10  # Time to wait for Chrome to exit gracefully
########################################################################
# Main logic and functions

# Function to log messages
log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "started: $app for $batch_id and $program_name" 

# Checking if Chrome is running
if pgrep "$app" > /dev/null; then
    log_msg "$app is running. Sending SIGTERM to terminate gracefully..."
    pkill -15 "$app"  # Send SIGTERM to allow graceful shutdown

    # Wait for a maximum of timeout_seconds for Chrome to exit
    for ((i = 0; i < timeout_seconds; i++)); do
        if ! pgrep "$app" > /dev/null; then
            log_msg "$app has exited gracefully."
            break
        fi
        sleep 1
    done

    # If Chrome is still running, force termination
    if pgrep "$app" > /dev/null; then
        log_msg "$app did not exit gracefully. Forcing termination..."
        pkill -9 "$app"  # Send SIGKILL as a last resort
    fi
else
    log_msg "No $app sessions are running."
fi

log_msg "completed: $app for $batch_id and $program_name" 

# Play audio files
#if [[ -f "$wake_mp3" ]]; then
#    $audio_app "$wake_mp3" &
#else
#    log_msg "Error: Wake MP3 file not found at $wake_mp3"
#fi

#if [[ -f "$desktop_mp3" ]]; then
#    $audio_app "$desktop_mp3" &
#else
#    log_msg "Error: Desktop MP3 file not found at $desktop_mp3"
#fi

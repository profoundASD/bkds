#!/bin/bash

########################################################################
# BKDS Chrome Kiosk Mode Launcher with Locking Mechanism
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
audio_path="$BKDS_UTIL_MP3"
wake_mp3="$audio_path/bkdsStartupSound.mp3"
audio_file="$audio_path/bkdsHomePage.mp3"
audio_app="mpg123"

# Locking Mechanism Variables
lock_dir="$BKDS_AUTO_SCHED_LOCKS"
lock_file="$lock_dir/${batch_id}.lastrun"
min_wait_time=4  # Minimum wait time in seconds

# Browser settings
browser="google-chrome"
target_url="http://localhost:3000"
chrome_options_kiosk="--kiosk --password-store=basic"

# Node.js service check settings
node_check_url="http://localhost:3000"
node_check_interval=0.05
node_ready_delay=0.05

########################################################################
# Functions

log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

is_recent_submission() {
    if [ -f "$lock_file" ]; then
        last_run_time=$(cat "$lock_file")
        current_time=$(date +%s)
        elapsed_time=$((current_time - last_run_time))
        if [ "$elapsed_time" -lt "$min_wait_time" ]; then
            log_msg "Submission blocked: Last run was $elapsed_time seconds ago. Minimum wait is $min_wait_time seconds."
            return 0  # Recent submission found
        fi
    fi
    return 1  # No recent submission or lock file missing
}

update_lock_file() {
    mkdir -p "$lock_dir"
    date +%s > "$lock_file"
    log_msg "Lock file updated at $(cat "$lock_file")."
}

is_chrome_running() {
    pgrep -f "chrome.*--kiosk" > /dev/null
    return $?
}

kill_chrome() {
    pkill -f "chrome.*--kiosk"
}

start_chrome() {
    "$browser" $chrome_options_kiosk "$target_url" &
    log_msg "Chrome launched with $target_url."
}

is_node_service_running() {
    curl -s --head --request GET "$node_check_url" | grep "200 OK" > /dev/null
    return $?
}

wait_for_node_service() {
    while ! is_node_service_running; do
        sleep "$node_check_interval"
    done
    sleep "$node_ready_delay"
}

play_audio() {
    if command -v "$audio_app" &> /dev/null; then
        "$audio_app" "$wake_mp3" &
        "$audio_app" "$audio_file" &
    fi
}

########################################################################
# Main Logic

# Prevent obsessive submissions using lock mechanism
if is_recent_submission; then
    log_msg "Exiting: Script submission too soon after the last run."
    exit 0
fi

# Update lock file for this execution
update_lock_file

log_msg "Starting home page launcher."

if is_chrome_running; then
    kill_chrome
    start_chrome
else
    wait_for_node_service
    #play_audio
    start_chrome
fi

log_msg "Home page launcher process completed."

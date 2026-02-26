#!/bin/bash
# Triggers keyring and prompts user to enter password with prompt ready for input
# enables user to have 1 key pw entry to system with special keyboard

#####################################################################
# Main Setup / Variables
#Get the base name of the file
program_name="$(basename "${0%.*}")"
batch_id=$1
#shell scripts used
log_script=$BKDS_UTIL_PYTHON/bkds_LogMsg.py
#other files/settings used
target_page="http://reload.extensions/"
browser_options="--headless --disable-gpu --start-minimized"
sleep_duration=$2
########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

# Function to start Chrome headlessly and capture its PID
start_chrome_headless() {
  google-chrome $browser_options $target_page
  CHROME_PID=$!
}

# Function to kill Chrome gracefully by PID
kill_chrome() {
  if [ -n "$CHROME_PID" ]; then
    kill -15 "$CHROME_PID"  # Graceful termination signal (SIGTERM)
    wait "$CHROME_PID"
  fi
}

# Main function
main() {
  log_msg "headless chrome launching for $duration"
  start_chrome_headless #triggers unlock prompt to user
  sleep "$sleep_duration"
  kill_chrome
  log_msg "headless chrome terminated after $duration"
}
# Run the main function
main

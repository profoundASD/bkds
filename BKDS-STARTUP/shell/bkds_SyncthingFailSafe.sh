#!/bin/bash
#####################################################################
# Usage:
# Description:
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1

#scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
#other files/settings used
syncthing_service='syncthing@jason.service'

########################################################################
#  Main logic and functions

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}
# Check if syncthing is running
if pgrep syncthing >/dev/null; then
  log_msg "syncthing is already running"
else
  # Start syncthing as a background process
  systemctl --user start $syncthing_service
  
  # Wait up to 300 seconds for syncthing to start
  for i in {1..15}; do
    
    if pgrep syncthing >/dev/null; then
      log_msg "syncthing is running"
      exit 0
    else
        systemctl --user start $syncthing_service
        #sudo systemctl start syncthing.service
    fi
    sleep 20
  done

  # If syncthing did not start within 300 seconds, print an error message and exit with an error code
  log_msg "syncthing did not start within 300 seconds"
  exit 1
fi
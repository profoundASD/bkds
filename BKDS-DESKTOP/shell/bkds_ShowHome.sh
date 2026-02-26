#!/bin/bash
########################################################################
# BKDS
# Purpose: Navigate to main app page in kiosk mode without restarting Chrome
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
#insight_id=$2 #--currently unused
#shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
# Target URL
target_page="http://localhost:3000"

########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "Navigating to home page... $target_page"

# Find the Chrome window
chrome_window_id=$(xdotool search --onlyvisible --class "chrome" | head -n 1)

if [ -z "$chrome_window_id" ]; then
    log_msg "Error: Chrome is not running or no window found."
    exit 1
fi

# Focus on the Chrome window
xdotool windowactivate "$chrome_window_id"

# Simulate pressing Ctrl+L to focus the address bar
xdotool key ctrl+l

# Type the target URL
xdotool type "$target_page"

# Press Enter to navigate
xdotool key Return

log_msg "Navigation to $target_page completed."

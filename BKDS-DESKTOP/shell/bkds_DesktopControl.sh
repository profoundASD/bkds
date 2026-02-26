#!/bin/bash
########################################################################
# BKDS System Script Launcher
# This script executes various system utility scripts based on the command provided.
#
# Usage:
#   ./scriptLauncher.sh [BatchID] [CommandKey] 
########################################################################

# Main Setup / Variables
source "$BKDS_UTIL_SHELL/bkds_desktop_CommonFunctions.sh"

# Set base variables
program_name="$(basename "${0%.*}")"
batch_id="$1"
command="$2"

# Python script for logging
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"

# Shell scripts used
shell_path="$BKDS_DESKTOP_SHELL" 
power_center_script="$shell_path/bkds_PowerControls.sh"
home_app_script="$shell_path/bkds_HomeButton.sh"
show_desktop_script="$shell_path/bkds_ShowDesktop.sh"
update_system_script="$shell_path/bkds_UpdateSoftware.sh"

# Other settings/files used
power_center_sleep_key="POWER_SLEEP"
power_center_restart_key="POWER_REBOOT"
power_center_shutdown_key="POWER_SHUTDOWN"
desktop_key="DESKTOP_SHOW"
home_key="HOME_APP"
update_key="UPDATE_CHECK"

########################################################################
#  Main logic and functions

log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1" 
}

log_msg "starting: $command for $batch_id and $program_name"

# Execute the appropriate script based on the command key
# append the key to batch id for downstream logging/reporting
case "$command" in
    "$home_key")
        bash "$home_app_script" "$batch_id"_"$home_key" 
        ;;
    "$power_center_sleep_key")
        bash "$power_center_script" "$batch_id"_"$power_center_sleep_key" "$power_center_sleep_key" &
        ;;
    "$power_center_restart_key")
        bash "$power_center_script" "$batch_id"_"$power_center_restart_key" "$power_center_restart_key" 
        ;;
    "$power_center_shutdown_key")
        bash "$power_center_script" "$batch_id"_"$power_center_shutdown_key" "$power_center_shutdown_key" 
        ;;
    "$desktop_key")
        bash "$show_desktop_script" "$batch_id"_"$desktop_key" 
        ;;
    "$update_key")
        bash "$update_system_script" "$batch_id"_"$update_key" 
        ;;
    *)
        log_msg "Unknown command: $command. Exiting."
        exit 1
        ;;
esac

log_msg "completed: $command for $batch_id and $program_name"
#!/bin/bash
########################################################################
# BKDS System Script Launcher
# Executes system utility scripts at specified intervals.
#
# Usage:
#   ./bkdsMainAutomationLoop.sh Sinterval_wait
########################################################################

# Set base variables
program_name="$(basename "${0%.*}")"
interval_wait_override=$1
max_intervals=$2
batch_id="$3""_AUTOMATION_MASTER"

#scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
auto_script="$BKDS_AUTO_SCHED_PYTHON/bkds_jobScheduler.py"
#automation config
data_path="$BKDS_AUTO_SCHED_DATA"
auto_args="$data_path/bkds_jobSchedule.json"
auto_config="$data_path/bkds_AutomationConfig.json"
#other settings/files used
# User input or hardcoded defaults
interval_wait_override=$1
max_intervals_override=$2
default_interval_wait=3
default_max_intervals=1000
# Assigning with fallback to defaults
interval_wait=${interval_wait_override:-$default_interval_wait}  # Use first argument or default to 300 seconds
max_intervals=${max_intervals_override:-$default_max_intervals}  # Use second argument or default to 100

interval_time_unit="seconds"
########################################################################
# Main logic and functions

# Logging function
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo $1
}

# Read values from JSON file, use jq to parse JSON
if [ -f "$auto_config" ]; then
    interval_wait=$(jq -r '.interval_wait // empty' "$auto_config")
    max_intervals=$(jq -r '.max_intervals // empty' "$auto_config")
fi
# Set to default if values are empty
interval_wait=${interval_wait:-$default_interval_wait}
max_intervals=${max_intervals:-$default_max_intervals}

# Main loop
log_msg "Starting $batch_id for $max_intervals @ $interval_wait $interval_time_unit"
for (( i = 0; i < max_intervals; i++ )); do
    python3 "$auto_script" "$auto_args"
    log_msg "Cycle $i complete"
    sleep $interval_wait
done
log_msg "$auto_script completed for $batch_id executing $i intervals at $interval_wait $interval_time_unit"

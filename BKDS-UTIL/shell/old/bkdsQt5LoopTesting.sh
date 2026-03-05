#!/bin/bash
########################################################################
# BKDS System Script Launcher
# This script executes various system utility scripts based on the command provided.
#
# Usage:
#   ./bkdsQt5LoopTesting.sh [BatchID] [ConfigFile] 
########################################################################
# Main Setup / Variables
# Check if the required arguments are provided 
batch_id=$1

python_path="$BKDS_DESKTOP_PYTHON"
shell_path="$BKDS_DESKTOP_SHELL"
data_path="$BKDS_UTIL_DATA/json"

insight_shutdown_script="$shell_path/bkdsQt5OverlayShutdown.sh"
qt5_gen_script="bkdsInsightOverlayGenerator.py"
qt5_config_file="$data_path/bkdsQt5InsightMaster.json"
auto_qt5_config_file="$data_path/bkdsLoopTest.json"
current_loop=0
max_loops=50
loop_sleep_time=30

########################################################################
# Main logic and processing
echo "using: $qt5_config_file"
echo "using: $auto_config_file"
echo "loop sleep time: $loop_sleep_time"
echo "max_loops: $max_loops"

# Function to handle insights
function handle_insights() {
    insights=$(jq -c '.[] | select(.insight_status == "active")' "$qt5_config_file")

    # Kill the Python scripts if they are already running
    bash $insight_shutdown_script
    echo "shut down current desktop insights and widgets attempted"

    # Loop through each active insight and start the Python script
    for insight in $insights; do
        insight_id=$(echo $insight | jq -r '.insight_id')
        echo "handling $insight_id for $batch_id"
        python3 "$python_path/$qt5_gen_script" "$batch_id" "$insight_id" &
        echo "$insight_id handled"
    done

    echo "$python_path/$qt5_gen_script $batch_id $insight_id"
}

# Check Config File Readability
if [ ! -r "$qt5_config_file" ]; then
    echo "Qt5 Config file '$qt5_config_file' not found or not readable."
    exit 1
fi

if [ ! -r "$auto_qt5_config_file" ]; then
    echo "Auto Qt5 Config file '$auto_qt5_config_file' not found or not readable."
    exit 1
fi

while true; do
    echo "current cycle: $current_loop"

    current_loop=$((current_loop + 1))

    # Read sleep and loop parameters from the auto config file
    loop_sleep_time=$(jq -r '.[0].loop_sleep_time' "$auto_qt5_config_file")
    max_loops=$(jq -r '.[0].max_loops' "$auto_qt5_config_file")

    echo "Starting loop $current_loop with loop_sleep_time=$loop_sleep_time seconds and max_loops=$max_loops..."

    handle_insights
    mminTime=-1
    # Sleep for the specified loop time, checking for config changes
    start_time=$(date +%s)
    while true; do
        sleep 0.25  # Sleep for 1 second
        current_time=$(date +%s)
        elapsed_time=$((current_time - start_time))

        # Check if the config file has been updated during sleep
        if [ -n "$(find "$python_path/$qt5_gen_script" -mmin $mminTime)" ]; then
            echo "Config file updated on iteration $current_loop"
            echo "new configs: $auto_config_file"
            loop_sleep_time=$(jq -r '.[0].loop_sleep_time' "$auto_qt5_config_file")
            max_loops=$(jq -r '.[0].max_loops' "$auto_qt5_config_file")
            current_loop=0  # Reset the loop count
            sleep 3
            break
        fi

        # Check if the maximum number of loops has been reached
        if [ "$current_loop" -ge "$max_loops" ]; then
            echo "Maximum number of loops reached. Exiting..."
            exit 0
        fi

        # If elapsed time reaches loop_sleep_time, break the inner loop and continue the main loop
        if [ "$elapsed_time" -ge "$loop_sleep_time" ]; then
            # Read sleep and loop parameters from the auto config file again
            loop_sleep_time=$(jq -r '.[0].loop_sleep_time' "$auto_qt5_config_file")
            max_loops=$(jq -r '.[0].max_loops' "$auto_qt5_config_file")
            break
        fi
    done
done
#!/bin/bash

# Check if the required arguments are provided
#if [ "$#" -ne 1 ]; then
#    echo "Usage: $0 <config_json_file>"
#    exit 1
#fi
batch_id=$1

config_file="$BKDS_UTIL_DATA/json/bkdsLoopTest.json"
shell_path="$BKDS_DESKTOP_SHELL"
loop_script="$shell_path/bkdsDesktopControl.sh"
args1=$batch_id
args2="HOME_APP"

current_loop=0
loop_sleep_time=1  # Initial loop sleep time in seconds (1 second)
watch_file_path="/var/www/nginx/html"
watch_file="$watch_file_path/bkds_nginx_index.html"

# Function to calculate MD5 checksum of the config file
calculate_checksum() {
    md5sum "$watch_file" | awk '{print $1}'
}

old_checksum=$(calculate_checksum)

while true; do
    echo "looping: $current_loop and watching $watch_file"
    current_loop=$((current_loop + 1))

    # Check if the config JSON file exists and is readable
    if [ -r "$config_file" ]; then
        # Read loop_sleep_time and max_loops from the JSON file
        loop_sleep_time=$(jq -r '.loop_sleep_time' "$config_file")
        max_loops=$(jq -r '.max_loops' "$config_file")

        echo "loop sleep time: $loop_sleep_time"
        echo "max_loops: $max_loops"

        echo "$loop_script"
        bash "$loop_script" "$args1" "$args2"

        # Calculate the number of iterations for half-second intervals
        half_second_iterations=$((loop_sleep_time * 2))

        echo "Starting loop $current_loop with loop_sleep_time=$loop_sleep_time seconds and max_loops=$max_loops..."

        # Check if the config file has been updated during sleep
        for ((i = 0; i < half_second_iterations; i++)); do
            echo "listening for metadata changes to $watch_file"
            new_checksum=$(calculate_checksum)
            if [ "$new_checksum" != "$old_checksum" ]; then
                echo "$watch_file updated. Restarting after $current_loop cycles..."
                current_loop=0  # Reset the loop count
                old_checksum="$new_checksum"  # Update the checksum
                break
            fi

            # Check if the maximum number of loops has been reached
            if [ "$current_loop" -ge "$max_loops" ]; then
                echo "Maximum number of loops reached. Exiting..."
                break
            fi
            sleep 0.5  # Sleep for half a second
        done

        # Check if the maximum number of loops has been reached
        if [ "$current_loop" -ge "$max_loops" ]; then
            echo "Maximum number of loops reached. Exiting..."
            break
        fi
    else
        echo "Config file '$watch_file' not found or not readable."
        exit 1
    fi
done

#!/bin/bash

# Check if the required arguments are provided
#if [ "$#" -ne 1 ]; then
#    echo "Usage: $0 <config_json_file>"
#    exit 1
#fi
batch_id=$1
insight_id=$2
config_file="$BKDS_UTIL_DATA/json/bkdsLoopTest.json"
current_loop=0
python_path="$BKDS_DESKTOP_PYTHON"
insight_shutown_script="$BKDS_DESKTOP_SHELL/bkdsQt5OverlayShutdown.sh"
insight_id1="INSIGHT_QT5_OVERLAY_LEFT_1"
insight_id2="INSIGHT_QT5_OVERLAY_LEFT_2"
insight_id2_5="INSIGHT_QT5_OVERLAY_LEFT_2.5"
insight_id3="INSIGHT_QT5_OVERLAY_LEFT_3"
insight_id3_5="INSIGHT_QT5_OVERLAY_LEFT_3.5"
insight_id4="INSIGHT_QT5_OVERLAY_LEFT_4"
insight_id5="INSIGHT_QT5_OVERLAY_RIGHT_1"
insight_id6="INSIGHT_QT5_OVERLAY_RIGHT_2"
insight_id7="INSIGHT_QT5_OVERLAY_RIGHT_3"
insight_id8="INSIGHT_QT5_OVERLAY_RIGHT_4"
insight_id9="INSIGHT_QT5_OVERLAY_RIGHT_5"
insight_id10="INSIGHT_QT5_OVERLAY_RIGHT_6"
insight_id11="INSIGHT_QT5_OVERLAY_RIGHT_7"
insight_id12="INSIGHT_QT5_OVERLAY_CENTER_1"
insight_id13="INSIGHT_QT5_OVERLAY_ICON_CALL"
insight_id14="INSIGHT_QT5_OVERLAY_ICON_MORE_APPS"
insight_id15="INSIGHT_QT5_OVERLAY_ICON_CALL_PHOTOS"


loop_script="bkdsInsightOverlayGenerator.py"

while true; do
    echo "looping: $current_loop with $insight_id"
    current_loop=$((current_loop + 1))

    # Check if the config JSON file exists and is readable
    if [ -r "$config_file" ]; then
        # Read loop_sleep_time and max_loops from the JSON file
        loop_sleep_time=$(jq -r '.loop_sleep_time' "$config_file")
        max_loops=$(jq -r '.max_loops' "$config_file")
        echo "loop sleep time: $loop_sleep_time"
        echo "max_loops: $max_loops"
        
        # Kill the Python scripts if they are already running
        #pkill -f "python3 $python_path/bkdsInsightOverlayRight.py" $batch_id $insight_id &
        #pkill -f "python3 $python_path/bkdsInsightOverlayLeft.py" $batch_id $insight_id &
        bash $insight_shutown_script
        # Run the Python scripts in the background and redirect their output
        #python3 "$python_path/bkdsInsightOverlayRight.py" $batch_id $insight_id &
        python3 "$python_path/$loop_script" $batch_id $insight_id1 &
        python3 "$python_path/$loop_script" $batch_id $insight_id2 &
        python3 "$python_path/$loop_script" $batch_id $insight_id2_5 &
        python3 "$python_path/$loop_script" $batch_id $insight_id3 &
        python3 "$python_path/$loop_script" $batch_id $insight_id3_5 &
        python3 "$python_path/$loop_script" $batch_id $insight_id4 &
        python3 "$python_path/$loop_script" $batch_id $insight_id5 &
        python3 "$python_path/$loop_script" $batch_id $insight_id6 &
        python3 "$python_path/$loop_script" $batch_id $insight_id7 &
        python3 "$python_path/$loop_script" $batch_id $insight_id8 &
        python3 "$python_path/$loop_script" $batch_id $insight_id9 &
        python3 "$python_path/$loop_script" $batch_id $insight_id10 &
        python3 "$python_path/$loop_script" $batch_id $insight_id11 &
        python3 "$python_path/$loop_script" $batch_id $insight_id12 &
        python3 "$python_path/$loop_script" $batch_id $insight_id13 &
        python3 "$python_path/$loop_script" $batch_id $insight_id14 &
        python3 "$python_path/$loop_script" $batch_id $insight_id15 &

        #echo "$python_path/bkdsInsightOverlayRight.py"
        echo "$python_path/$loop_script"
        sleep 5
        echo "Starting loop $current_loop with loop_sleep_time=$loop_sleep_time seconds and max_loops=$max_loops..."

        # Sleep for the specified loop time
        sleep "$loop_sleep_time"

        # Check if the config file has been updated during sleep
        if [ -n "$(find "$config_file" -mmin -1)" ]; then
            echo "Config file updated. Restarting loop..."
            current_loop=0  # Reset the loop count
        fi

        # Check if the maximum number of loops has been reached
        if [ "$current_loop" -ge "$max_loops" ]; then
            echo "Maximum number of loops reached. Exiting..."
            break
        fi
    else
        echo "Config file '$config_file' not found or not readable."
        exit 1
    fi
done

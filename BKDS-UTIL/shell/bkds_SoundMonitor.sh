#!/bin/bash
########################################################################
# BKDS 
# Purpose: check sound settings
########################################################################
# Main Setup / Variables
base_name="$(basename "${0%.*}")"
batch_id=$1

shell="bash"
python="python3"

#shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
set_volume_script="$BKDS_UTIL_SHELL/bkds_SetVolume.sh"

usb_dir="/sys/bus/usb/devices/*"
########################################################################
#  Main logic and functions

log_msg() {
   $python $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

LOG_DIR="$BKDS_UTIL_LOGS"
TIMESTAMP=$(date '+%Y%m%d%H%M%S')
LOG_FILE="${LOG_DIR}/${program_name}_${batch_id}_${TIMESTAMP}.log"
# Initialize flag for changed audio
CHANGED="F"
# Get the current active sink
ACTIVE_SINK=$(pactl list sinks | grep -B 1 "State: RUNNING" | head -1 | awk '{print $2}')
# Get all available sinks
AVAILABLE_SINKS=$(pactl list short sinks | awk '{print $2}')
# Get the current audio sink
CURRENT_SINK=$(pactl info | grep "Default Sink" | awk '{print $3}')
# Find the device's bus and device number
DEVICE=$(lsusb | grep "${VID}:${PID}" | awk '{print $2,$4}' | tr -d ':')
# Vendor and Product ID from lsusb
VID="1908"
PID="2070"
# Find the device's bus and device number
DEVICE=$(lsusb | grep "${VID}:${PID}" | awk '{print $2,$4}' | tr -d ':')
# Extract bus and device number
BUS=$(echo $DEVICE | awk '{print $1}')
DEV=$(echo $DEVICE | awk '{print $2}')
# Find the corresponding directory in /sys/bus/usb/devices/
for DIR in $usb_dir; do
    if [[ -e "${DIR}/idVendor" && -e "${DIR}/idProduct" ]]; then
        CURRENT_VID=$(cat "${DIR}/idVendor")
        CURRENT_PID=$(cat "${DIR}/idProduct")
        
        if [[ "${CURRENT_VID}" == "${VID}" && "${CURRENT_PID}" == "${PID}" ]]; then
            # Reset the USB device
            echo 0 | sudo tee "${DIR}/authorized"
            echo 1 | sudo tee "${DIR}/authorized"
            break
        fi
    fi
done

ACTIVE_SINK=$(pactl list sinks | grep -B 1 "State: RUNNING" | head -1 | awk '{print $2}')
# Log the results
{
    log_msg "Changed Audio: $CHANGED"
    log_msg "Current Audio: $ACTIVE_SINK"
    log_msg -e "\nAvailable Audio:"
    log_msg "$AVAILABLE_SINKS"
    log_msg -e "\nAll Devices\n\n"
    log_msg "$(lsusb)"
} > $LOG_FILE
# Only keep the most recent 20 log files
OLD_LOGS=$(ls -t1 ${LOG_DIR}hjSound_*.log | tail -n +21)
if [[ ! -z "$OLD_LOGS" ]]; then
    echo "$OLD_LOGS" | xargs rm --
fi

$shell $set_volume_script $batch_id
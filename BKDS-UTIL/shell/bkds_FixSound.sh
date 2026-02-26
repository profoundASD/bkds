#!/bin/bash
########################################################################
# BKDS 
# Purpose: Re-adjust sound settings
########################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
initial_vol=${2:-50}  # Use the second argument or default to 50%

# Shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"

# Other settings/files
usb_dir="/sys/bus/usb/devices/*"
# Vendor and Product ID from lsusb
VID="1908"
PID="2070"

audio_app='pactl'
audio_sink='@DEFAULT_SINK@'

########################################################################
# Main logic and functions

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "fix sound start"

# Unmute the audio sink
log_msg "Unmuting audio sink"
$audio_app set-sink-mute $audio_sink 0

# Set the volume to the initial volume or default to 50%
log_msg "Setting volume to ${initial_vol}%"
$audio_app set-sink-volume $audio_sink "${initial_vol}%"

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

# Allow some time for PulseAudio to recognize the device after resetting
sleep 1

log_msg "fix sound end"

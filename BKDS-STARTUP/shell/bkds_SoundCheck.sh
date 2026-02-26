#!/bin/bash
#####################################################################
# Usage:
# Description:
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1

# Shell scripts used
shell_path="$BKDS_UTIL_SHELL"
fix_sound_script="$BKDS_UTIL_SHELL/bkds_FixSound.sh"
volume_adjust_script="$shell_path/bkds_VolumeAdjust.sh"

#volume_speak_script="$shell_path/bkds_AudioGen.sh"

log_script=$BKDS_UTIL_PYTHON/bkds_LogMsg.py

$tts_prefix='bkds_util_soundCheck_tts_'
# Other settings/files used
initial_vol="35"  # Correctly format the volume adjustment argument
vol_dir='-d r'
########################################################################
# Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "Starting audio configuration..."

# Step: Check if PulseAudio is running, and start it if necessary
log_msg "Checking PulseAudio status..."
if ! pulseaudio --check 2>/dev/null; then
    log_msg "PulseAudio not running. Attempting to start PulseAudio..."
    pulseaudio --start
    sleep 1  # Allow some time for PulseAudio to initialize
    if ! pulseaudio --check 2>/dev/null; then
        log_msg "Error: PulseAudio could not be started."
        exit 1
    else
        log_msg "PulseAudio successfully started."
    fi
else
    log_msg "PulseAudio is already running."
fi

# List all available audio output devices
devices=$(pacmd list-sinks | grep -e 'index:' -e 'description:' | awk '{if ($1 == "index:") printf "%s;", $2; else printf "%s\n", substr($0, index($0,$3));}' | tr '[:upper:]' '[:lower:]')

# Loop through each device and check if it meets the criteria
default_device=""
log_msg "default_device before: $default_device"

for device in $devices; do
    log_msg "Checking devices..."
    
    # Exclude devices with "microphone", "unitek", or "pdif" in the description
    if [[ $device == *"microphone"* || $device == *"unitek"* || $device == *"pdif"* ]]; then
        log_msg "Checked mic: $device"
        continue
    fi

    # Select the first USB device with "standard" in the description
    if [[ $device == *"standard"* && $device == *"usb"* ]]; then
        log_msg "standard USB: $device"
        default_device=$(echo $device | cut -d';' -f1)
        break
    fi

    # Select the first HDMI or 3.5mm device available
    if [[ $device == *"hdmi"* || $device == *"analog-output"* ]]; then
        if [[ -z $default_device ]]; then
            log_msg "analog output: $device"        
            default_device=$(echo $device | cut -d';' -f1)
        fi
    fi
done

log_msg "default_device after: $default_device"

log_msg "checking sinks"
sleep 0.25

# Check if the default device needs to be set
current_device=$(pacmd list-sinks | grep -e 'index:' -e 'description:' -e 'active port:' | awk '{if ($1 == "index:") {printf "%s:", $2} else if ($1 == "description:") {printf "%s\n", $0} else if ($1 == "active") {printf "%s:", $3} else if ($1 == "port:") {printf "%s\n", substr($0, index($0,$2))}}' | grep -E '^(index:|description:|active:|port:)' | tr '\n' ';')
if [[ $current_device == *"$default_device;"* ]]; then
    log_msg "Current default audio output is already set to device $default_device"
else
    pacmd set-default-sink $default_device
    log_msg "Default audio output set to device $default_device"
fi

bash $fix_sound_script $batch_id $initial_vol

# Reset volume and display/speak setting to user
log_msg "adjusting volume started"
bash $volume_adjust_script $batch_id $initial_vol &
sleep 1
#bash $volume_speak_script $batch_id $tts_prefix $initial_vol &
log_msg "adjusting volume done"

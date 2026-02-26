#!/bin/bash
########################################################################
# Script Name: bkds_mouseSettings.sh
# Usage: ./bkds_mouseSettings.sh <batch_id>
# Description: Identifies a mouse device matching a pattern, checks its
#              current button mapping, and remaps only if needed,
#              using settings from a JSON configuration file.
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
hostname=$(hostname)
batch_id="${1:-default}"

# Global Constants
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"  # Path to logging script
config_file="${BKDS_UTIL_DATA:-$HOME/.config/bkds}/config/bkds_input_device_settings.json"  # Path to JSON config file
xinput_command="/usr/bin/xinput"                # Command to manage input devices

# Logging Function
log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

########################################################################
# Validate Environment
log_msg "Running on hostname: $hostname"

if ! command -v "$xinput_command" &> /dev/null; then
    log_msg "Error: xinput is not installed or not in PATH."
    exit 1
fi

# Create config directory if it doesn't exist
config_dir=$(dirname "$config_file")
mkdir -p "$config_dir"

# Check if the config file exists, create it if it doesn't
if [ ! -f "$config_file" ]; then
    log_msg "Config file not found: $config_file. Creating it."
    cat <<EOF > "$config_file"
{
    "device_name_pattern": "Eagle",
    "device_type": "pointer",
    "default_button_map": "1 1 1 4 5 6 7"
}
EOF
    log_msg "Config file created: $config_file"
fi

# Read configuration from JSON file
search_pattern=$(jq -r '.device_name_pattern' "$config_file")
device_type=$(jq -r '.device_type' "$config_file")
default_button_map=$(jq -r '.default_button_map' "$config_file")

# Validate configuration
if [ -z "$search_pattern" ] || [ -z "$device_type" ] || [ -z "$default_button_map" ]; then
    log_msg "Error: Invalid or missing configuration in $config_file"
    exit 1
fi

########################################################################
# Identify Matching Device
log_msg "Searching for devices matching pattern: $search_pattern"

# Get the list of pointer devices
device_list=$("$xinput_command" list | grep "$device_type" | grep "$search_pattern")
if [ -z "$device_list" ]; then
    log_msg "No devices matching pattern '$search_pattern' found. Exiting gracefully."
    exit 0
fi

# Extract the device ID from the matched line
device_id=$(echo "$device_list" | grep -oP 'id=\K[0-9]+')
if [ -z "$device_id" ]; then
    log_msg "Error: Failed to retrieve device ID for pattern '$search_pattern'."
    exit 1
fi

log_msg "Device found: $search_pattern (ID: $device_id)"

########################################################################
# Get Current Button Mapping
log_msg "Retrieving current button mapping for device ID $device_id"
current_button_map=$("$xinput_command" get-button-map "$device_id" 2>/dev/null | tr -s ' ' | sed 's/ $//')

if [ $? -ne 0 ]; then
    log_msg "Error: Failed to retrieve button mapping for device ID $device_id."
    exit 1
fi

log_msg "Current button mapping: $current_button_map"

########################################################################
# Check and Apply Button Mapping
if [ "$current_button_map" == "$default_button_map" ]; then
    log_msg "No change needed. Button mapping is already set to: $default_button_map"
else
    log_msg "Applying new button mapping: $default_button_map"
    "$xinput_command" set-button-map "$device_id" $default_button_map

    if [ $? -eq 0 ]; then
        log_msg "Successfully updated button mapping to: $default_button_map"
    else
        log_msg "Error: Failed to update button mapping for device ID $device_id."
        exit 1
    fi
fi

########################################################################
# Confirm New Button Mapping
new_button_map=$("$xinput_command" get-button-map "$device_id" 2>/dev/null | tr -s ' ' | sed 's/ $//')

log_msg "New button mapping: $new_button_map"

if [ "$new_button_map" == "$default_button_map" ]; then
    log_msg "Mouse remapping completed successfully."
else
    log_msg "Error: Button mapping verification failed. Current mapping: $new_button_map"
    exit 1
fi

exit 0
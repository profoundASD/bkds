#!/bin/bash
########################################################################
# BKDS
# Purpose: Set the system hostname based on a JSON configuration file.
#          Creates the JSON config file with a default hostname if it
#          doesn't exist. Handles network updates after changing the
#          hostname. Exits early if the hostname is already correct.
#
# Usage: bash setHostName.sh <batch_id>
#####################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id="${1:-default}"
current_hostname=$(hostname)

# Python scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
max_attempts=10
attempt=0

# Default hostname
default_hostname="bkds-demo-app"

# Configuration file path
config_file="${BKDS_UTIL_DATA:-$HOME/.config/bkds}/config/bkds_node_id.json"

########################################################################
# Main logic and functions

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1"
    echo "$1"
}

# Ensure the config directory exists
config_dir=$(dirname "$config_file")
mkdir -p "$config_dir"

# Check if the config file exists, create it with the default hostname if it doesn't
if [ ! -f "$config_file" ]; then
    log_msg "Config file not found: $config_file. Creating it with default hostname."
    echo "{ \"preferred_hostname\": \"$default_hostname\" }" > "$config_file"
    log_msg "Config file created: $config_file"
    pref_hostname="$default_hostname"
else
    # Read preferred hostname from JSON config file
    pref_hostname=$(jq -r '.preferred_hostname' "$config_file")
    if [ -z "$pref_hostname" ]; then
        log_msg "Error: Could not read preferred hostname from config file: $config_file"
        exit 1
    fi
    log_msg "Preferred hostname read from config: $pref_hostname"
fi

log_msg "Current node id: $current_hostname"

# Check if the current hostname matches the desired hostname
if [ "$current_hostname" == "$pref_hostname" ]; then
    log_msg "$current_hostname is already set to $pref_hostname"
    echo "$current_hostname"
    exit 0  # Exit early if hostname is already correct
fi

# Wait for the hostname to be set correctly (only if it was not already correct)
while [ $attempt -lt $max_attempts ] && { [ "$current_hostname" == "localhost" ] || [ "$current_hostname" == "localhost.localdomain" ] || [ "$current_hostname" == "127.0.0.1" ] || [ "$current_hostname" == "127.0.1.1" ] || [ -z "$current_hostname" ] ; }; do
    log_msg "Attempt $attempt: Waiting for a valid hostname (current: $current_hostname)"
    sleep 1
    attempt=$((attempt + 1))
    current_hostname=$(hostname)
done

# Check if the maximum number of attempts was reached
if [ $attempt -ge $max_attempts ]; then
    log_msg "Error: Maximum attempts reached. Hostname is not set correctly."
fi

log_msg "$program_name is comparing $current_hostname to $pref_hostname"

# Check if the current hostname matches the desired hostname (again, after waiting)
if [ "$current_hostname" != "$pref_hostname" ]; then
    log_msg "Changing $current_hostname to $pref_hostname"

    # Set the new hostname
    sudo hostnamectl set-hostname "$pref_hostname"
    if [ $? -eq 0 ]; then
        log_msg "Hostname changed successfully to $pref_hostname"

        # Update /etc/hosts (if applicable)
        sudo sed -i "s/127.0.1.1.*$current_hostname/127.0.1.1\t$pref_hostname/g" /etc/hosts

        # Update current_hostname variable after successful change
        current_hostname=$(hostname)

        # Restart networking (method depends on the OS)
        if command -v systemctl &> /dev/null; then
            log_msg "Restarting networking service using systemctl..."
            sudo systemctl restart systemd-networkd # Or whichever service manages networking on your system
        elif command -v service &> /dev/null; then
            log_msg "Restarting networking service using service..."
            sudo service networking restart # Or the appropriate service name
        elif command -v /etc/init.d/* &> /dev/null; then
           log_msg "Restarting networking using init.d script"
           sudo /etc/init.d/networking restart
        else
            log_msg "Warning: Could not determine how to restart networking."
        fi
    else
        log_msg "Error setting hostname. Check sudo permissions and hostnamectl availability."
    fi
else
    log_msg "$current_hostname is already set to $pref_hostname"
fi

# Return the current hostname
echo "$current_hostname"
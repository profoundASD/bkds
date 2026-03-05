#!/bin/bash

# Get hostname from JSON file
NEW_HOSTNAME=$(jq -r '.hostname' "$BKDS_UTIL_DATA/config/bkds_node_id.json")

# Syncthing directories and files
SYNCTHING_CONFIG_DIR="$HOME/.config/syncthing"
SYNCTHING_KEY_FILES=("cert.pem" "key.pem")
SYNCTHING_SERVICE="syncthing"

# Chrome directory
CHROME_DIR="$HOME/.config/google-chrome"
CHROME_SINGLETON_PATTERN="Singleton*"

# Function to log messages
log_msg() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Stop Syncthing
log_msg "Stopping Syncthing service..."
systemctl --user stop $SYNCTHING_SERVICE || log_msg "Failed to stop Syncthing service."

# Stop networking
log_msg "Stopping networking..."
sudo systemctl stop NetworkManager || log_msg "Failed to stop NetworkManager."

# Backup and delete Syncthing key files
log_msg "Backing up and deleting Syncthing key files..."
mkdir -p "$SYNCTHING_CONFIG_DIR/backup"
for file in "${SYNCTHING_KEY_FILES[@]}"; do
    if [ -f "$SYNCTHING_CONFIG_DIR/$file" ]; then
        mv "$SYNCTHING_CONFIG_DIR/$file" "$SYNCTHING_CONFIG_DIR/backup/"
        log_msg "Backed up $file to $SYNCTHING_CONFIG_DIR/backup/"
    else
        log_msg "Key file $file not found in $SYNCTHING_CONFIG_DIR."
    fi
done

# Set hostname
log_msg "Setting hostname to $NEW_HOSTNAME..."
sudo hostnamectl set-hostname "$NEW_HOSTNAME" || log_msg "Failed to set hostname."

# Update /etc/hosts file
log_msg "Updating /etc/hosts file..."
if grep -q "$NEW_HOSTNAME" /etc/hosts; then
    log_msg "Hostname already exists in /etc/hosts."
else
    echo "127.0.0.1 $NEW_HOSTNAME" | sudo tee -a /etc/hosts || log_msg "Failed to update /etc/hosts."
fi

# Flush network and DNS cache
log_msg "Flushing network and DNS cache..."
sudo systemctl restart systemd-resolved || log_msg "Failed to restart systemd-resolved."
sudo ip addr flush dev $(ip route | grep default | awk '{print $5}') || log_msg "Failed to flush IP addresses."

# Delete Google Chrome singleton files
log_msg "Deleting Google Chrome singleton files..."
if [ -d "$CHROME_DIR" ]; then
    find "$CHROME_DIR" -name "$CHROME_SINGLETON_PATTERN" -exec rm -f {} \;
    log_msg "Deleted Chrome singleton files in $CHROME_DIR."
else
    log_msg "Google Chrome directory $CHROME_DIR not found."
fi

# Restart networking
log_msg "Restarting networking..."
sudo systemctl start NetworkManager || log_msg "Failed to start NetworkManager."

# Start Syncthing
log_msg "Starting Syncthing service..."
systemctl --user start $SYNCTHING_SERVICE || log_msg "Failed to start Syncthing service."

log_msg "Setup process completed."
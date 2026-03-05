#!/bin/bash
#####################################################################
# Usage: ./start_nodemon.sh
# Description:
#   This script launches Nodemon for the Node.js application while
#   ignoring non-development files such as images and logs.
#####################################################################

# Main Setup / Variables
program_name=$(basename "$0")
batch_id='BKDS_NODEJS_APP'
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
app_dir="$BKDS_NODEJS"
node_script="$BKDS_APP/BKDS-NODEJS/bkds_main_node.js"
memory_limit=6144
required_watch_limit=524288

# Files and directories to ignore
ignored_files=(
    "*.png" "*.jpg" "*.jpeg" "*.gif" "*.log" "node_modules" "dist" "logs" "*.tmp"
)

# Watch patterns for specific `.json` files
watch_patterns=(
    "public/data/**/*_batch.json"
    "public/data/**/*_feed.json"
)

# Function for logging
log_msg() {
    python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

# Increase inotify watch limit if needed
log_msg "Checking and updating inotify watch limit..."
current_watch_limit=$(cat /proc/sys/fs/inotify/max_user_watches)
if (( current_watch_limit < required_watch_limit )); then
    sudo sysctl -w fs.inotify.max_user_watches=$required_watch_limit
    echo "fs.inotify.max_user_watches=$required_watch_limit" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
    log_msg "Increased inotify watch limit to $required_watch_limit."
else
    log_msg "Inotify watch limit is sufficient: $current_watch_limit."
fi

# Check and change to the application directory
if [ -d "$app_dir" ]; then
    cd "$app_dir" || exit 1
    log_msg "Changed directory to: $app_dir"
else
    log_msg "Error: Application directory $app_dir does not exist."
    exit 1
fi

# Verify Node.js script exists
if [ ! -f "$node_script" ]; then
    log_msg "Error: Node.js script $node_script does not exist."
    exit 1
fi

# Construct Nodemon command
nodemon_cmd=(
    "nodemon"
    "--max-old-space-size=$memory_limit"
)

# Add ignore patterns
for pattern in "${ignored_files[@]}"; do
    nodemon_cmd+=("--ignore" "$pattern")
done

# Add watch patterns
for pattern in "${watch_patterns[@]}"; do
    nodemon_cmd+=("--watch" "$pattern")
done

nodemon_cmd+=("$node_script")

# Start Nodemon
log_msg "Launching Nodemon with the following command: ${nodemon_cmd[*]}"
"${nodemon_cmd[@]}"
log_msg "Nodemon started successfully in the background."

exit 0

#!/bin/bash
########################################################################
# Script Name: bkds_content_gen_runner.sh
# Usage: ./bkds_content_gen_runner.sh <batch_id>
# Description: Runs a specific content generation script based on 
#              JSON configuration for the provided batch ID.
#
# Arguments:
#   batch_id  A unique identifier for the batch to be processed.
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
hostname=$(hostname)
echo "Running on hostname: $hostname"

python="python3"

# Paths
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
config_file="$BKDS_UTIL_DATA/config/bkds_contentGen.json"

# Ensure batch_id is provided
if [ -z "$batch_id" ]; then
    echo "Error: batch_id argument is missing."
    echo "Usage: $0 <batch_id>"
    exit 1
fi

########################################################################
# Logging function
log_msg() {
    $python "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

########################################################################
# Load Configuration
log_msg "Loading configuration for batch_id: $batch_id"

if [ ! -f "$config_file" ]; then
    log_msg "Error: Configuration file $config_file not found."
    exit 1
fi

# Extract type, script_path, and script for the specific batch_id
script_info=$($python -c "
import json, sys, os
try:
    with open('$config_file') as f:
        data = json.load(f)
        entry = data.get('$batch_id', {})
        if not entry:
            sys.exit(1)
        script_path = os.path.expandvars(entry.get('script_path', ''))
        print(f\"{entry.get('type', '')} {script_path} {entry.get('script', '')}\")
except Exception as e:
    sys.exit(1)
")

# Validate script_info
if [ -z "$script_info" ]; then
    log_msg "Error: No valid script configuration found for batch_id: $batch_id"
    exit 1
fi

script_type=$(echo "$script_info" | awk '{print $1}')
script_path=$(echo "$script_info" | awk '{print $2}')
script_name=$(echo "$script_info" | awk '{print $3}')
full_script_path="$script_path/$script_name"

log_msg "Script Type: $script_type, Script Path: $script_path, Script Name: $script_name"

# Ensure the script exists
if [ ! -f "$full_script_path" ]; then
    log_msg "Error: Script $script_name not found at $full_script_path."
    exit 1
fi

########################################################################
# Run the Script
case "$script_type" in
    python)
        log_msg "Executing Python script: $full_script_path"
        $python "$full_script_path" "$batch_id"
        ;;
    bash)
        log_msg "Executing Bash script: $full_script_path"
        bash "$full_script_path" "$batch_id"
        ;;
    *)
        log_msg "Error: Unsupported script type '$script_type' for $script_name"
        exit 1
        ;;
esac

# Check execution status
if [ $? -eq 0 ]; then
    log_msg "Execution of $script_name completed successfully."
else
    log_msg "Error: Execution of $script_name failed."
    exit 1
fi

log_msg "Script execution finished."
exit 0

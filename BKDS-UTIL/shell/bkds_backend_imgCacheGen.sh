#!/bin/bash
################################
# Automated Content Generation and Database Integration Script
#
# This script performs automated content generation for image caching and
# integrates the generated content into a PostgreSQL database.
# It accepts a batch ID as an argument, runs a Python script to generate
# image caches, and then loads the data into the database.
#
# Usage:
#   ./script_name.sh <batch_id>
#
# Arguments:
#   batch_id: Unique identifier for the batch processing
################################

# Check for the correct number of arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <batch_id>"
    exit 1
fi

################################
# Main Setup Variables begin
batch_id="$1"
program_name="$(basename "${0%.*}")"
shell="bash"
python="python3"

# Environment variables
python_path="$BKDS_UTIL_PYTHON"
shell_path="$BKDS_UTIL_SHELL"

#scripts
imgCache_script="$python_path/bkds_backend_imgCacheGenGet.py"
#imgCacheLoad_script="$shell_path/bkds_imgCacheGenLoad.sh"
log_script="$python_path/bkds_LogMsg.py"

# Commands
imgCache="$python $imgCache_script $batch_id"
#dbLoad="$shell $imgCacheLoad_script $batch_id"
app1="image cache generation"
app2="database load"

# Main Setup Variables end
################################

##############################
# functions and processing

# Function to log messages
log_msg() {
    local message="$1"
    echo "[$(date)] $message"
    python3 "$log_script" "$program_name" "$batch_id" "$message"
}

# Image cache generation begin
log_msg "Starting $logmsg1 with with batch: $batch_id"

# Execute the image cache generation script
log_msg "Executing: $imgCache"
if eval $imgCache; then
    log_msg "Successfully completed $app1"
else
    log_msg "Error: $app1 failed"
    exit 1
fi

# Execute the database load script
#log_msg "Executing $app2"

#if eval $dbLoad; then
#    log_msg "Successfully completed $app2"
#else
#    log_msg "Error: $dbLoad failed"
#    exit 1
#fi

#log_msg "$imgCacheLoad_script completed successfully"

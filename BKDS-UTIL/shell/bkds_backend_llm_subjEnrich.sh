#!/bin/bash

#####################################################################
# Description: Automates text extraction and enrichment using OpenAI's language model.
#####################################################################

# Ensure at least two arguments are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <batch_id_process> <batch_id_api> [loops]"
    exit 1
fi

# Command-line arguments
batch_id_process=$1
batch_id_api=$2
loops=${3:-1}  # Default to 1 loop if not provided
max_wait=8     # Max random wait in seconds between iterations

# Debug: Log received arguments
echo "Debug: Received arguments"
echo "batch_id_process: $batch_id_process"
echo "batch_id_api: $batch_id_api"
echo "loops: $loops"

# Program and environment setup
program_name="$(basename "${0%.*}")"

# Check required environment variables
if [ -z "$BKDS_UTIL_PYTHON" ] || [ -z "$BKDS_UTIL_DATA" ]; then
    echo "Error: Required environment variables 'BKDS_UTIL_PYTHON' or 'BKDS_UTIL_DATA' are not set."
    echo "BKDS_UTIL_PYTHON: $BKDS_UTIL_PYTHON"
    echo "BKDS_UTIL_DATA: $BKDS_UTIL_DATA"
    exit 1
fi

# Debug: Log environment variables
echo "Debug: Environment variables"
echo "BKDS_UTIL_PYTHON: $BKDS_UTIL_PYTHON"
echo "BKDS_UTIL_DATA: $BKDS_UTIL_DATA"

# Paths and files
python_path="$BKDS_UTIL_PYTHON"
config_file_path="$BKDS_UTIL_DATA/config/bkds_backend_llm_ProcessFlow.json"
log_script="$python_path/bkds_LogMsg.py"
python_script_process="$python_path/bkds_backend_llm_ProcessFlow.py"
python_script_dbLoad="$python_path/bkds_backend_llm_DBload_Hygiene.py"

# Verify required Python scripts
if [ ! -f "$python_script_process" ]; then
    echo "Error: Python script $python_script_process not found. Exiting."
    exit 1
fi

if [ ! -f "$python_script_dbLoad" ]; then
    echo "Error: Python script $python_script_dbLoad not found. Exiting."
    exit 1
fi

# Debug: Log script paths
echo "Debug: Paths and files"
echo "Python path: $python_path"
echo "Config file: $config_file_path"
echo "Log script: $log_script"
echo "Process script: $python_script_process"
echo "DB Load script: $python_script_dbLoad"

# Logging function
logMsg() {
    local message="$1"
    echo "[$(date)] $message"
    python3 "$log_script" "$program_name" "$batch_id_process" "$message"
}

#####################################################################
# Main logic with loop control
#####################################################################

for ((i = 1; i <= loops; i++)); do
    logMsg "Starting iteration $i of $loops for batch_id_process: $batch_id_process, batch_id_api: $batch_id_api"

    # Run the processing script
    logMsg "Running process script: $python_script_process"
    echo "Debug: Executing command:"
    echo "python3 $python_script_process --batch_id_process $batch_id_process --batch_id_api $batch_id_api --config_path $config_file_path"
    if ! python3 "$python_script_process" --batch_id_process "$batch_id_process" --batch_id_api "$batch_id_api" --config_path "$config_file_path"; then
        logMsg "Error: Processing script failed on iteration $i. Exiting."
        exit 1
    fi

    # Run the DB load script
    logMsg "Running DB load script: $python_script_dbLoad"
    echo "Debug: Executing DB load command:"
    echo "python3 $python_script_dbLoad --batch_id $batch_id_process --config_key $batch_id_process --config_path $config_file_path"
    if ! python3 "$python_script_dbLoad" --batch_id "$batch_id_process" --config_key "$batch_id_process" --config_path "$config_file_path"; then
        logMsg "Error: DB load script failed on iteration $i. Exiting."
        exit 1
    fi

    # Random sleep interval between iterations
    if [ "$i" -lt "$loops" ]; then
        random_sleep=$((RANDOM % max_wait + 1))
        logMsg "Pausing for $random_sleep seconds before next iteration..."
        sleep "$random_sleep"
    fi
done

logMsg "All loops completed successfully."
exit 0

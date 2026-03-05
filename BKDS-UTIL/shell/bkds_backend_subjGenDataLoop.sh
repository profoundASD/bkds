#!/bin/bash
################################
# Script for Automated Batch Subject Generation
# This script repeatedly executes a given command at specified intervals,
# up to a maximum number of times. It is designed for batch processing
# in content generation systems.
#
# Usage: $0 <script_name> <wait_sec> <max_loop> <data_env> [<subj_type>]
# Example:
#   bash script.sh bkds_subjGenData.sh 5 10
#   bash script.sh bkds_subjGenData.sh 5 10 my_environment flickr
#
# - script_name: Name of the shell script to execute
# - wait_sec: Interval in seconds between each command execution
# - max_loop: Maximum number of iterations for the loop
# - data_env: Environment variable (batch ID for logic/logging)
# - subj_type (optional): Subject type (e.g., flickr)
################################

# Parameter Check
if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
    echo "Usage: $0 <script_name> <wait_sec> <max_loop> <batch_id> [<subj_type>]"
    exit 1
fi

################################
# Main Setup Variables
program_name="$(basename "${0%.*}")"

# Script Parameters
script_name=$1  # Name of the shell script to execute
wait_sec=$2  # Time interval in seconds
max_loop=$3  # Maximum number of iterations
batch_id=$4  # Batch ID for logic/logging
subj_type=${5:-}  # Subject type, optional

script_path="$BKDS_UTIL_SHELL/$script_name"

# Construct command to execute
if [ -n "$subj_type" ]; then
    command="bash $script_path $batch_id $subj_type"
else
    command="bash $script_path $batch_id"
fi

# Loop Counter
counter=0
#
################################

##############################
# Subject Generation Loop Begin

while [ $counter -lt $max_loop ]
do
    echo "Executing iteration $((counter+1))"
    echo "using command: $command"
    eval $command
    ((counter++))

    # Wait for specified interval
    sleep $wait_sec
done

echo "Loop completed. Executed $counter times."

# Subject Generation Loop End
##############################

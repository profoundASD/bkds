#!/bin/bash

#####################################################################
# Description: This script is a wrapper for the bkds_subjGenEnrichContent.py program. 
# It automates the extraction, enrichment, and storage of textual insights using OpenAI's language model.
# The script fetches data from a PostgreSQL view, enriches it, and then loads the results into a database.
#
# Usage: ./bkds_subjGenEnrichContentWrapper.sh <batch_id>
#
# Arguments:
#   <batch_id>: Unique identifier for the batch processing session.
#
# Example:
#   ./bkds_SubjEnrich.sh helloworld1234
#
# Note: Requires environment variables for database credentials and OpenAI API key.
#####################################################################
# Main Setup / Variables


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <batch_id>"
    exit 1
fi


batch_id=$1
program_name="$(basename "${0%.*}")"

# Environment Variables
if [ -z "$BKDS_NODEJS_DATA_SUBJ" ] || [ -z "$BKDS_UTIL_PYTHON" ]; then
    echo "Required environment variables not set. Exiting."
    exit 1
fi

python_path="${BKDS_UTIL_PYTHON}"
log_script="$python_path/bkdsLogMsg.py"
python_script="$python_path/bkds_subjGenEnrichContent.py"


########################################################################
# Main logic and functions

# Logging function
logMsg() {
    echo "[$(date)] $1"
    python3 $log_script "$program_name" "$batch_id" "$1"
}

logMsg "Starting $python_script from $program_name"
python3 $python_script "$batch_id" || { logMsg "$program_name failed"; exit 1; }
logMsg "Completed $python_script from $program_name"
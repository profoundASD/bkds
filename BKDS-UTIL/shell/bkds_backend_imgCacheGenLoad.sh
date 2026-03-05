#!/bin/bash
################################

################################
# main setup variables
batch_id="$1"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <batch_id>"
    exit 1
fi

# Environment variables
python_path="$BKDS_UTIL_PYTHON"
program_name="$(basename "${0%.*}")"
shell="bash"
python="python3"

#scripts
imgCache_dbLoad_script="$python_path/bkds_backend_imgCacheGen_DBLoad.py"
dbLoad="$python $imgCache_dbLoad_script $batch_id"
log_script="$python_path/bkds_LogMsg.py"

#
################################
# functions and processing

log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" 
}

##############################
# DB Load begin

log_msg "dbload using $dbLoad with $batch_id"

eval $dbLoad || log_msg "$dbLoad failed with $batch_id"

log_msg "completed $dbLoad with $batch_id"

# DB Load end
##############################
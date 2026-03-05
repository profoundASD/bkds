#!/bin/bash
################################

################################
# main setup variables
data_dir="$1"
type="$2"

# Environment variables
program_name="$(basename "${0%.*}")"
python_path="$BKDS_UTIL_PYTHON_BACKEND_CONTENT"
python="python3"

#scripts
subjGen_dbLoad_script="$python_path/bkds_dbload_subjGenAPIResults.py"
dbLoad="$python $subjGen_dbLoad_script $data_dir $type"
log_script="$python_path/bkds_LogMsg.py"

app1='database load'

#
################################
log_msg() {
    $python $log_script "$program_name" "$batch_id" "$1" 
}

##############################
# DB Load begin

log_msg "$app1 using $dbLoad with $type"

eval $dbLoad || log_msg "$dbLoad failed with $type"

log_msg "$app1 completed $dbLoad with $type"

# DB Load end
##############################
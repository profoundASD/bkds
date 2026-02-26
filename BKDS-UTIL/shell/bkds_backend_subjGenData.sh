#!/bin/bash
################################
#
# Header: Automated Content Generation and Database Integration Script
# 
# This script is designed for the automated generation of content based on a given index of subjects and integrates 
# the generated content into a specified database. It accepts a batch ID and a type identifier as inputs, 
# determining the nature of the content to be generated (e.g., wiki, YouTube, Flickr). 
# 
# The process includes validating script parameters, setting up environment variables, 
# executing subject generation scripts, and handling the loading of generated content into a database. 
# The script features robust logging mechanisms to track its progress and any issues that arise. 
# It is tailored for efficient batch processing in content management and database systems.
#
################################

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <batch_id> <data env> <type>"
    exit 1
fi

################################
# main setup variables
batch_id="$1"
env="$2"
type="$3"

program_name="$(basename "${0%.*}")"

# scripts and paths
python_path="$BKDS_UTIL_PYTHON"
log_script="$python_path/bkds_LogMsg.py"
subjGen_script="$python_path/bkds_backend_subjGenMain.py"
alt_subjGen_script="$python_path/bkds_backend_yt_HTMLParse.py"

shell_path="$BKDS_UTIL_SHELL"
subjGenLoad_script="$shell_path/bkds_backend_subjGenLoad.sh"

#args and commands
data_env=$env
subjGen="python3 $subjGen_script $data_env $type"
dbLoad="bash $subjGenLoad_script $data_env $type"

yt_key="yt"
yt_alt_key="yt_alt"
wiki_key="wiki"
flickr_key="flickr"

supported_types="wiki, youtube/yt/yt_alt, flickr"
#
################################

# Function to log messages
log_msg() {
    echo "[$(date)] $1"
    python3 "$log_script" "$program_name" "$batch_id" "$1"
}
#
###############################
## Subject Generation begin
#
log_msg "Starting $subjGen_script with $type"

declare -A subprocesses
##
case $type in
    wiki) 
        subprocesses[wiki_key]=1
        ;;
    youtube|yt|yt_alt) 
        if [ "$type" == $yt_alt_key ]; then
            subprocesses[yt_key]=1
            subjGen="python3 $alt_subjGen_script $batch_id"
        else
            subprocesses[yt_key]=1
        fi
        ;;
    flickr) 
        subprocesses[flickr_key]=1
        ;;
    *)
        echo "Invalid type: $type. Supported types: $supported_types."
        exit 1
        ;;
esac

#
# Execute required subprocesses
log_msg "Starting $subjGen using $type"
eval $subjGen || log_msg "$subjGen failed with $type"
log_msg "Finished $subjGen using $type"

# Subject Generation end
##############################

log_msg "$subjGen completed"
log_msg "$dbLoad beginning"

##############################
# DB Load begin

log_msg "dbload using $dbLoad"

eval $dbLoad || log_msg "$dbLoad failed with $type"

log_msg "completed $dbLoad with $type"

# DB Load end
##############################

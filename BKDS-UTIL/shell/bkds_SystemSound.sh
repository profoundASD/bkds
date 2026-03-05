#!/bin/bash
########################################################################
# BKDS 
# Purpose: check sound settings
########################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1

#env
shell="bash"
python="python3"

#shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
#audio used
audio_path="$BKDS_UTIL_MP3"
audio_file="$audio_path/bkdsStartupSound.mp3"
audio_app="mpg123"

########################################################################
#  Main logic and functions

log_msg() {
    $python $log_script "$program_name" "$batch_id" "$1" 
}

#log_msg "audio $audio_file started"
$audio_app "$audio_file"
#log_msg "audio $audio_file ended"

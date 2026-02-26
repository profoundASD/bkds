#!/bin/bash
########################################################################
# BKDS 
# Purpose: Go to main voice input app
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
insight_id=$2 #--currently unused

#shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
#files/settings used
target_page="http://localhost:3000/?startSpeech=true&type=voice_search_general"
browser_options="--kiosk"

########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

log_msg "opening voice search...$browser_options $target_page"
pkill chrome
sleep .10
google-chrome $browser_options $target_page

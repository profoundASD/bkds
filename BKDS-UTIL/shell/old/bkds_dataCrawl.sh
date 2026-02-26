#!/bin/bash
#####################################################################
# Usage:
# Description:
#####################################################################
# Main Setup / Variables
node_id="bkds-pc-00" #node_id separates backend reporting/logging 
program_name="$(basename "${0%.*}")"
batch_id="BKDS_${1}_STARTUP"

#shell scripts used - startup
pytho_path="$BKDS_UTIL_PYTHON"
wiki_script="$python_path/bkds_getWiki.py"

########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}
# Setup / Resetting env complete
########################################################################

########################################################################
# Conky App Launch Begin
# Launches soon to display during workspace transformation
# 
    log_msg "$wiki_script begins"
    bash $wiki_script $batch_id $node_id &
    log_msg "$wiki_script attempted"
# Conky App Launch end
########################################################################
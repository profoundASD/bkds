#!/bin/bash
#####################################################################
# Usage: ./generate_subject_insights.sh <batch_id>
# Description: This script processes subject insights generation for a given batch.
#              It launches subscripts to fetch and process data from various sources,
#              including subject indexing, Wikipedia, YouTube, and Flickr.
#####################################################################

# Main Setup / Variables
node_id=$(hostname)
program_name="$(basename "${0%.*}")"
batch_id="BKDS_SUBJ_GEN_${node_id}_${program_name}"

# Set the absolute path to the log script
log_script="$BKDS_UTIL_PYTHON/bkdsLogMsg.py"

# Set the absolute paths to the Python scripts
python_path="$BKDS_NODEJS_PYTHON"
#given a list of ID's, subj_index_script will search and find all Id's and build a single file for processing downstream
subj_index_script="$python_path/bkds_getSubjects.py" 
#the parent directory of all subject data files
subj_dir="$BKDS_NODEJS_PUBLIC/data/subjects" 
#id_file is input to subj_index_script and consists of subject/insight ID's to process within subj_dir
id_file="$BKDS_NODEJS_PUBLIC/data/config/bkds_insight_id_index.json" 
#index_wip_file is output of subj_index_script a consolidated file of insights/subjects to process given the ID's above
index_wip_file="$BKDS_NODEJS_PUBLIC/data/output/bkds_subj_index_wip.json" 

#scripts to get data given specific subjects
wiki_script="$python_path/bkds_getWiki.py"
yt_script="$python_path/bkds_getYouTube.py"
flickr_script="$python_path/bkds_getFlickr.py"

########################################################################
# Main logic and functions
log_msg() {
    echo "Logging: $1"  # Print log message to stdout
    python3 $log_script "$program_name" "$batch_id" "$1"  # Log the message
}

# Setup / Resetting env complete
########################################################################
# Debugging: Print the paths and environment variables
log_msg "script_dir: $script_dir"
log_msg "log_script: $log_script"
log_msg "python_path: $python_path"
log_msg "subj_index_script: $subj_index_script"
log_msg "wiki_script: $wiki_script"

log_msg "working with $index_wip_file" 
log_msg "working with $id_file" 
log_msg "working with $subj_dir" 

########################################################################
# Subj index Launch Begin
# Launches soon to display during workspace transformation
# 
log_msg "$subj_index_script begins"
python3 $subj_index_script $batch_id $id_file $subj_dir
log_msg "$subj_index_script attempted"
# Subj Index Launch end
########################################################################

# Check if the file exists
if [ -f "$index_wip_file" ]; then
    log_msg "found $index_wip_file" 

########################################################################
# Wiki Gen Launch Begin
# Launches soon to display during workspace transformation
# 
    log_msg "$wiki_script begins with $batch_id"
    python3 $wiki_script $batch_id $node_id $index_wip_file
    log_msg "$wiki_script ended"

# Wiki Gen Launch end
########################################################################

########################################################################
# YouTube Gen Launch Begin
# Launches soon to display during workspace transformation
# 
    log_msg "$yt_script begins with $batch_id"
    python3 $yt_script $batch_id $node_id $index_wip_file
    log_msg "$yt_script ends with $batch_id"
#
# YouTube Gen Launch End
########################################################################

########################################################################
# Flickr Gen Launch Begin
# Launches soon to display during workspace transformation
# 
    log_msg "$flickr_script begins with $batch_id"
    python3 $flickr_script $batch_id $node_id $index_wip_file
    log_msg "$flickr_script ends with $batch_id"
#
# Flickr Gen Launch End
########################################################################

else
    log_msg "Updated output file not found: $index_wip_file"
fi
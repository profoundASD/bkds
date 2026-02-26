#!/bin/bash
########################################################################
# BKDS Screenshot Capture Script with In-Memory Compression
# and No-Monitor Handling
########################################################################

# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=$1
hostname=$(hostname)
echo $hostname

python="python3"

# Shell path and scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
report_path="$BKDS_REPORTING_SCREENSHOTS"
output_dir="${report_path}/${hostname}/$(date +"%Y%m%d")/$batch_id"
output_img="$output_dir/${hostname}_${batch_id}_${program_name}_$(date +"%Y%m%d_%H%M%S").jpg"

########################################################################
# Logging function
log_msg() {
    $python "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
}

# Ensure dependencies are installed
if ! command -v scrot &> /dev/null; then
    log_msg "Error: scrot is not installed. Unable to take screenshot."
    exit 1
fi

if ! command -v convert &> /dev/null; then
    log_msg "Error: ImageMagick 'convert' is not installed. Unable to compress screenshot."
    exit 1
fi

# Check for an active display
if [ -z "$DISPLAY" ] && ! pgrep -x "Xorg" > /dev/null; then
    log_msg "No active display detected. Skipping screenshot."
    exit 0
fi

# Ensure the screenshot directory exists
if ! mkdir -p "$output_dir"; then
    log_msg "Error: Failed to create directory $output_dir"
    exit 1
fi

# Take screenshot and compress in-memory
log_msg "Taking screenshot and compressing in-memory"
if scrot -q 100 - | convert - -resize 1920x1080 -quality 60 "$output_img"; then
    # Log completion message
    log_msg "Screenshot captured, compressed, and saved as $output_img"
else
    log_msg "Error: Failed to capture or process screenshot."
    exit 1
fi
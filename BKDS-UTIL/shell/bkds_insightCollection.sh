#!/bin/bash
########################################################################
# BKDS Insight Gathering Script (Updated)
# 
# Purpose:
# Updates:
# 1. Considers the last 3 days for insights.
# 2. Ignores empty `.json` files.
# 3. Skips `.json` files with "ERROR" as the first key.
# 4. Excludes files matching the `*sync-conflict*` pattern.
########################################################################

# Check for batch_id argument
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <batch_id>"
    exit 1
fi

batch_id="$1"

# Paths and Variables
insight_index="$BKDS_UTIL_DATA/config/bkds_insight_index.json"
insights_dir="$BKDS_APP/BKDS-INSIGHTS/$(hostname)"
archive_dir="$insights_dir/archive"
age_limit=6000  # Files older than X minutes will be archived
# Ensure the insights and archive directories exist
mkdir -p "$insights_dir" "$archive_dir"

########################################################################
# Functions

log_msg() {
    local message=$1
    python3 "$BKDS_UTIL_PYTHON/bkds_LogMsg.py" "$(basename "${0%.*}")" "$batch_id" "$message" && echo "$message"
}

expand_vars() {
    local expanded_path
    expanded_path=$(echo "$1" | envsubst)
    echo "$expanded_path"
}

is_valid_json() {
    local file=$1
    # Check if the file is non-empty and does not have "ERROR" as the first key
    if [[ -s "$file" ]] && ! grep -q '"ERROR":' "$file"; then
        return 0  # Valid JSON
    fi
    return 1  # Invalid JSON
}

process_insight() {
    local insight_name=$1
    local raw_insight_path=$2
    local archive_type=$3
    local hostname=$(hostname)
    local insight_path

    # Expand placeholders in the insight path
    raw_insight_path=${raw_insight_path//@@_hostname_@@/$hostname}
    insight_path=$(expand_vars "$raw_insight_path")

    log_msg "Processing $insight_name insights from $insight_path"

    # Look back over the last 3 days
    for i in {0..2}; do
        local date=$(date -d "-${i} days" +%Y%m%d)
        local path_with_date=${insight_path//@@_DATE_YYYYMMDD_@@/$date}

        # Find latest valid .json files excluding *sync-conflict* pattern
        find "$path_with_date" -type f -name "*$insight_name*.json" ! -name "*sync-conflict*" 2>/dev/null | \
        while read -r file; do
            if is_valid_json "$file"; then
                local filename=$(basename "$file")

                if [[ ! -f "$insights_dir/$filename" ]]; then
                    cp "$file" "$insights_dir"
                    log_msg "Copied valid $insight_name insight: $filename to $insights_dir"
                else
                    log_msg "Skipped copying $filename (already exists)"
                fi
            else
                log_msg "Skipped invalid or error-containing file: $file"
            fi
        done
    done

    # Archive files older than the specified age limit
    local timestamp=$(date +%Y%m%d%H%M%S)
    local archive_file="$archive_dir/${archive_type}_archive_$timestamp.zip"

    find "$insights_dir" -maxdepth 1 -type f -mmin +"$age_limit" | while read -r old_file; do
        zip -q "$archive_file" "$old_file" && rm "$old_file"
        log_msg "Archived $old_file into $archive_file"
    done
}

archive_old_json_files() {
    local timestamp=$(date +%Y%m%d%H%M%S%3N)  # Include milliseconds in timestamp
    local archive_file="$archive_dir/$(basename "$0" .sh)_${batch_id}_${timestamp}.zip"

    # Find `.json` files older than the specified number of days
    find "$insights_dir" -type f -name "*.json" -mtime +"$archive_days" ! -name "*sync-conflict*" 2>/dev/null | while read -r old_file; do
        zip -q "$archive_file" "$old_file" && rm "$old_file"
        log_msg "Archived old JSON file: $old_file into $archive_file"
    done

    if [[ -f "$archive_file" ]]; then
        log_msg "Final archive created: $archive_file"
    else
        log_msg "No old JSON files found to archive."
    fi
}

########################################################################
# Main Logic

log_msg "Insight gathering process started"

jq -r 'to_entries[] | "\(.key) \(.value)"' "$insight_index" | while read -r insight_name insight_path; do
    process_insight "$insight_name" "$insight_path" "$batch_id"
done

# Final step: Archive old JSON files in the target directory
archive_old_json_files

log_msg "Insight gathering process completed"

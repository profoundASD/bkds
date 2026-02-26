#!/bin/bash
########################################################################
# File Archive Management Script
# This script facilitates recursive searching for specific file extensions
# in a target directory and archives files older than a specified number
# of days into a single archive file per batch. It supports excluding
# specific directories and file name patterns from the archiving process.
# It also ensures that files are not re-archived in subsequent runs.
# When the --delete flag is provided, it deletes files from the source
# location after they have been successfully archived.
#
# Usage: bash archive_files.sh <batch_id> <file_extension> <archive_time> [--delete]
########################################################################

# --- Main Setup ---
program_name="$(basename "${0%.*}")"
batch_id=$1
file_extension=$2
archive_time=$3
delete_flag=$4

file_extension="${file_extension#.}"  # Normalize file extension (remove leading dot)

# Required environment variables
: "${BKDS_APP:?Error: BKDS_APP environment variable is not set.}"
: "${BKDS_ARCHIVE:?Error: BKDS_ARCHIVE environment variable is not set.}"
: "${BKDS_NODEJS:?Error: BKDS_NODEJS environment variable is not set.}"
: "${BKDS_LOGS:?Error: BKDS_LOGS environment variable is not set.}"
: "${BKDS_UTIL_PYTHON:?Error: BKDS_UTIL_PYTHON environment variable is not set.}"

# Shell scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"

TARGET_DIR=$BKDS_APP
current_date="$(date +%Y%m%d)"
current_time="$(date +%H%M%S)"
ARCHIVE_DIR="$BKDS_ARCHIVE/$(hostname)/$current_date"
EXCLUDE_DIRS="$BKDS_NODEJS/node_modules,$BKDS_LOGS"
EXCLUDE_PATTERNS="_specific_archive1_,file_pattern2"
ARCHIVE_EXPIRATION_DAYS=3
ARCHIVED_FILES_LIST="$BKDS_ARCHIVE/$(hostname)/$current_date/bkds_archived_files_master.txt"  # Central list of all archived files

# --- Helper Functions ---

# Sanitize paths (remove trailing slashes)
sanitize_path() {
    echo "$1" | sed 's:/*$::'
}

log_msg() {
    if [ -x "$log_script" ]; then
        python3 "$log_script" "$program_name" "$batch_id" "$1" && echo "$1"
    else
        echo "$1"
    fi
}

check_directories() {
    if [ ! -d "$TARGET_DIR" ]; then
        log_msg "Error: TARGET_DIR does not exist: $TARGET_DIR"
        exit 1
    fi
    mkdir -p "$ARCHIVE_DIR" || { log_msg "Failed to create archive directory: $ARCHIVE_DIR"; exit 1; }
    touch "$ARCHIVED_FILES_LIST" # Ensure the master archived files list exists
}

build_find_command() {
    local ext=$1
    local find_cmd=(find "$TARGET_DIR")

    # Exclude directories (assuming they are absolute paths)
    if [ -n "$EXCLUDE_DIRS" ]; then
        IFS=',' read -ra dirs <<< "$EXCLUDE_DIRS"
        for dir in "${dirs[@]}"; do
            log_msg "Excluding directory: $dir" >&2
            find_cmd+=(-path "$dir" -prune -o)
        done
    fi

    # Append file type and extension filter, with quotes
    find_cmd+=(-type f -name "*.${ext}")

    # Add exclusion patterns
    if [ -n "$EXCLUDE_PATTERNS" ]; then
        IFS=',' read -ra patterns <<< "$EXCLUDE_PATTERNS"
        for pattern in "${patterns[@]}"; do
            log_msg "Excluding pattern: *${pattern}*" >&2
            find_cmd+=(! -name "*${pattern}*")
        done
    fi

    # Add file age condition
    find_cmd+=(-mmin +"$archive_time" -print0)

    log_msg "Final find command: ${find_cmd[*]}" >&2
    echo "${find_cmd[@]}"
}


archive_files() {
    local ext=$1
    log_msg "Starting archive_files for *.$ext files older than $archive_time minutes in $TARGET_DIR"

    # Construct the find command to get all eligible files
    local -a find_command_all=($(build_find_command "$ext"))

    # Filter out already archived files
    if [ -s "$ARCHIVED_FILES_LIST" ]; then
        log_msg "Excluding previously archived files" >&2

        # Prepare the -not -path arguments for already archived files
        local -a exclude_args
        while IFS= read -r archived_file; do
            exclude_args+=(-not -path "$archived_file")
        done < "$ARCHIVED_FILES_LIST"

        # Combine the original find command with the exclusion arguments
        local -a find_command_filtered=("${find_command_all[@]:0:${#find_command_all[@]}-1}")
        find_command_filtered+=("${exclude_args[@]}")
        find_command_filtered+=("${find_command_all[@]: -1}") # Add -print0 back at the end
    else
        # If no archived files, use the original find command
        local -a find_command_filtered=("${find_command_all[@]}")
    fi

    # Execute the find command and collect output
    local files_to_archive=()
    while IFS= read -r -d $'\0' file; do
        files_to_archive+=("$file")
    done < <("${find_command_filtered[@]}")

    # Check if any files are found
    if [ ${#files_to_archive[@]} -eq 0 ]; then
        log_msg "No new files to archive for batch ID: $batch_id"
        return
    fi

    # Create the archive
    local archive_file="$ARCHIVE_DIR/${batch_id}_${program_name}_${ext}_${current_date}_${current_time}.tar.gz"
    log_msg "Creating archive: $archive_file"

    # Use a process substitution to feed the null-terminated file list to tar
    tar -czvf "$archive_file" -T - < <(printf '%s\0' "${files_to_archive[@]}")

    if [[ $? -eq 0 ]]; then
        log_msg "Archive created successfully: $archive_file"

        # Append newly archived files to the central archived files list
        printf '%s\n' "${files_to_archive[@]}" >> "$ARCHIVED_FILES_LIST"

        # Delete the files if the --delete flag is set
        if [[ "$delete_flag" == "--delete" ]]; then
            log_msg "Deleting archived files from the source location"
            for file in "${files_to_archive[@]}"; do
                if grep -Fxq "$file" "$ARCHIVED_FILES_LIST"; then
                    rm "$file"
                    log_msg "Deleted: $file"
                else
                    log_msg "Not previously archived. Not deleting: $file"
                fi
            done
        fi
    else
        log_msg "Error creating archive: $archive_file"
    fi
}


delete_archived_files() {
    log_msg "Starting deletion of archived files from source locations"

    # Read the list of archived files
    if [ ! -s "$ARCHIVED_FILES_LIST" ]; then
        log_msg "No archived files found in the master list. Skipping deletion."
        return
    fi

    # Iterate through the list and delete each file
    while IFS= read -r -d $'\0' archived_file; do
        if [ -f "$archived_file" ]; then
            rm "$archived_file"
            log_msg "Deleted: $archived_file"
        else
            log_msg "File not found, could have been already deleted: $archived_file"
        fi
    done < <(tr '\n' '\0' < "$ARCHIVED_FILES_LIST")

    log_msg "Deletion of archived files complete."
}

cleanup_archive_dir() {
    log_msg "Starting cleanup of archive directory: $ARCHIVE_DIR"

    # Delete files based on size and age (as already implemented in the script)
    find "$ARCHIVE_DIR" -type f \( -name "*.zip" -o -name "*.tar" -o -name "*.gz" -o -name "*.txt" -o -name "*.json" \) -print0 | while IFS= read -r -d $'\0' file; do
        size=$(stat -c%s "$file")

        if (( size > 10*1024*1024*1024 )); then
            log_msg "Deleting immediately (over 10GB): $file"
            rm "$file"
        elif (( size > 4*1024*1024*1024 )) && [[ $(find "$file" -mmin +$((72*60)) -print) ]]; then
            log_msg "Deleting (over 4GB and older than 72 hours): $file"
            rm "$file"
        elif (( size > 420*1024*1024 )) && [[ $(find "$file" -mmin +$((5*24*60)) -print) ]]; then
            log_msg "Deleting (over 420MB and older than 5 days): $file"
            rm "$file"
        elif (( size > 40*1024*1024 )) && [[ $(find "$file" -mmin +$((13*24*60)) -print) ]]; then
            log_msg "Deleting (over 40MB and older than 13 days): $file"
            rm "$file"
        elif (( size > 5*1024*1024 )) && [[ $(find "$file" -mmin +$((25*24*60)) -print) ]]; then
            log_msg "Deleting (over 5MB and older than 25 days): $file"
            rm "$file"
        elif [[ $(find "$file" -mtime +60 -print) ]]; then
            log_msg "Deleting (older than 60 days): $file"
            rm "$file"
        fi
    done
    
    log_msg "ARCHIVE ROLL OFF CHECK BEGINS FOR: $ARCHIVE_DIR"

    # Determine the parent directory of $ARCHIVE_DIR
    local parent_dir
    parent_dir=$(dirname "$ARCHIVE_DIR")

    log_msg "Checking for directories older than $ARCHIVE_EXPIRATION_DAYS days in parent directory: $parent_dir"

    # Delete directories in the parent directory older than $ARCHIVE_EXPIRATION_DAYS
    find "$parent_dir" -mindepth 1 -maxdepth 1 -type d -mtime +"$ARCHIVE_EXPIRATION_DAYS" -print | while IFS= read -r old_dir; do
        log_msg "Handling: $old_dir"
        if rm -rf "$old_dir"; then
            log_msg "Deleted archive folder: $old_dir"
        else
            log_msg "Failed to delete archive folder: $old_dir"
        fi
    done

    log_msg "ARCHIVE ROLL OFF CHECK COMPLETE FOR: $parent_dir"

    log_msg "Cleanup of archive directory complete."
}


# --- Main Logic ---

# Validate input arguments
if [ -z "$batch_id" ] || [ -z "$file_extension" ] || [ -z "$archive_time" ]; then
    log_msg "Usage: $program_name <batch_id> <file_extension> <archive_time> [--delete]"
    exit 1
fi

log_msg "File archive script started for batch ID: $batch_id, file extension: .$file_extension"
log_msg "File archive script targeting directory: $TARGET_DIR"
log_msg "Archiving files to: $ARCHIVE_DIR"

# Check target and archive directories
check_directories

# Perform archiving
archive_files "$file_extension"

# Delete archived files if the --delete flag is set
if [[ "$delete_flag" == "--delete" ]]; then
    delete_archived_files
fi

cleanup_archive_dir

log_msg "File archive script completed for batch ID: $batch_id"
exit 0
#!/bin/bash

# Directory to start from
base_dir="/home/aimless76/Documents/Sync/BKDS/BKDS_APP/tmp-data"

# Function to clean up filenames
clean_filename() {
    local file_path="$1"
    local base_name=$(basename "$file_path")
    local dir_name=$(dirname "$file_path")

    # Remove leading and trailing apostrophes and replace spaces, hyphens, and other special characters with underscores
    local new_base_name=$(echo "$base_name" | sed "s/^'//; s/'$//; s/[ ,'-]/_/g; s/__*/_/g")

    if [[ "$base_name" != "$new_base_name" ]]; then
        mv -n "$file_path" "$dir_name/$new_base_name"
    fi
}

export -f clean_filename

# Use find to iterate over each file and rename as necessary
find "$base_dir" -type f -print0 | while IFS= read -r -d '' file; do
    clean_filename "$file"
done

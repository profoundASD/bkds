#!/bin/bash

base_dir_path="/home/aimless76/Documents/Sync/BKDS/BKDS_APP/tmp-data/Aviation"
base_dir_name=$(basename "$base_dir_path")

find "$base_dir_path" -depth -name "*[ ,'-]*" -print0 | while IFS= read -r -d '' file; do
    # Process each segment of the path to remove new lines and apostrophes
    new_name=""
    old_IFS=$IFS
    IFS='/'
    for segment in $file; do
        clean_segment=$(echo "$segment" | tr -d '\n'"'")
        if [ "$clean_segment" != "$base_dir_name" ]; then
            new_name="$new_name/$clean_segment"
        fi
    done
    IFS=$old_IFS
    new_name=$(echo "$new_name" | sed 's/ /_/g; s/-/_/g; s/,/_/g; s/'"'"'/_/g')

    # Remove the first slash added in new_name
    new_name=${new_name:1}

    echo "$new_name"
    if [ "$file" != "$new_name" ]; then
        # Extract directory from new name
        target_dir=$(dirname "$new_name")

        # Create target directory if it does not exist
        mkdir -p "$target_dir"

        # Check if $file is a directory and copy accordingly
        if [ -d "$file" ]; then
            cp -r "$file" "$new_name"  # Use -r for directories
        else
            cp "$file" "$new_name"  # Normal copy for files
        fi
    fi
done

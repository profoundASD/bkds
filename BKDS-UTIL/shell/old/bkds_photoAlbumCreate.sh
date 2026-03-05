#!/bin/bash

# Define source and destination directories
destination_dir="$HOME/Pictures/UPLOAD"
source_dir="$HOME/Documents/Sync/BKDS/BKDS-APP/BKDS-NODEJS/public/data/images/full_size/wiki"

# Set the cutoff date (formatted as YYYY-MM-DD)
cutoff_date="2024-11-03"

# Create the main UPLOAD directory if it doesn't exist
mkdir -p "$destination_dir"

# Find and copy files
find "$source_dir" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | while read -r file; do
   # echo "Reading..$file"

  # Check the modification date of the file
  file_mod_date=$(date -r "$file" +"%Y-%m-%d")
  if [[ "$file_mod_date" > "$cutoff_date" ]]; then
    # Get the relative path from the source directory
    relative_path="${file#$source_dir/}"
    folder_structure=$(dirname "$relative_path")

    # Create the corresponding folder structure in the destination directory
    #mkdir -p "$destination_dir/$folder_structure"

    # Copy the file to the destination while preserving the folder structure
    cp "$file" "$destination_dir/$folder_structure/"
    echo "Copied $file to $destination_dir/$folder_structure/"
  fi
done

echo "All files meeting the criteria have been copied."

#!/bin/bash

# Script: find_and_archive_bad_images.sh
# Usage: ./find_and_archive_bad_images.sh [optional_path_to_search]

# Default search path if no argument is provided
search_dir="${1:-$BKDS_NODEJS_DATA/images}"

# Output directory and files
output_dir="${BKDS_UTIL_DATA}/output"
output_file="${output_dir}/bad_images.json"
archive_file="${output_dir}/bad_images_archive.zip"

if [ -z "$search_dir" ] || [ -z "$BKDS_UTIL_DATA" ]; then
  echo "Error: Either BKDS_NODEJS_DATA or BKDS_UTIL_DATA is not set, and no path argument was provided."
  exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Initialize JSON array
echo "[" > "$output_file"

# Counters for processed and found files
count=0
found=0

# Temporary directory for archiving
temp_dir=$(mktemp -d)

# Find and process files
find "$search_dir" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -print0 | while IFS= read -r -d '' file; do
  ((count++))

  # Check if the file contains "File not found:"
  if strings "$file" | grep -q "File not found:"; then
    file_name=$(basename "$file")
    file_extension="${file_name##*.}"

    # Format file details as JSON object and append to the output file
    if (( found > 0 )); then
      echo "," >> "$output_file"  # Add comma for JSON formatting after the first entry
    fi
    echo "  {\"full_path\": \"$file\", \"file_name\": \"$file_name\", \"file_extension\": \"$file_extension\"}" >> "$output_file"
    
    # Move file to temp archive directory
    mv "$file" "$temp_dir/"

    ((found++))
  fi

  # Show progress every 100 files checked
  if (( count % 100 == 0 )); then
    echo -ne "Processed $count files...\r"
  fi
done

# Close the JSON array
echo "]" >> "$output_file"

# Create ZIP archive of all archived images
zip -j "$archive_file" "$temp_dir"/*

# Clean up temporary archive directory
rm -rf "$temp_dir"

# Print final counts
echo -e "\nFinished processing $count files. Found and archived $found bad images."
echo "Results saved to $output_file"
echo "Archive created at $archive_file"

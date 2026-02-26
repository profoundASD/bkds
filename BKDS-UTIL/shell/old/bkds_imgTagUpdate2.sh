#!/bin/bash

# Define paths
img_json_path="$BKDS_NODEJS_DATA/images/master_image_photos_index.json"
base_img_path="$BKDS_NODEJS_PUBLIC"

# Set the cutoff date (formatted as YYYY-MM-DD)
cutoff_date="2024-11-03"

# Initialize a counter
counter=1

# Parse JSON file and loop through each image entry
jq -c '.[]' "$img_json_path" | while read -r image; do
  # Construct the full path for the image and replace spaces with underscores
  img_path="$base_img_path$(echo "$image" | jq -r '.img_url' | sed 's/ /_/g')"

  # Check if the file path or name contains '_yt_', '_youtube_', or is in a 'youtube' folder
  if [[ "$img_path" == *"/youtube/"* || "$img_path" == *"_yt_"* || "$img_path" == *"_youtube_"* ]]; then
    #echo "Skipping file due to 'youtube' criteria: $img_path"
    continue
  fi

  # Check if the file modification date is newer than the cutoff date
  file_mod_date=$(date -r "$img_path" +"%Y-%m-%d")
  if [[ "$file_mod_date" > "$cutoff_date" ]]; then
    #echo "Skipping file due to modification date newer than $cutoff_date: $img_path"
    continue
  fi

 
  # Extract metadata fields from the JSON object
  img_title=$(echo "$image" | jq -r '.img_title')
  img_desc1=$(echo "$image" | jq -r '.img_desc1')
  img_desc2=$(echo "$image" | jq -r '.img_desc2')

  # Extract data_category and format: replace spaces with ", ", underscores with spaces
  img_data_category=$(echo "$image" | jq -r '.data_category | .[0:5] | join(" ")' | sed -e 's/ /, /g' -e 's/_/ /g')

  # Extract data_subject and format: replace spaces with ", ", underscores with spaces
  img_data_subject=$(echo "$image" | jq -r '.data_subject | .[0:5] | join(" ")' | sed -e 's/ /, /g' -e 's/_/ /g')

  # Print status message
  echo "Processing image #$counter: $img_path"

  # Add metadata to the image using ExifTool
# Add metadata to the image using ExifTool, ignoring minor warnings
exiftool -m -overwrite_original \
  -Title="$img_title" \
  -Description="$img_desc1 $img_desc2" \
  -Keywords="$img_data_category" \
  -Subject="$img_data_subject" \
  "$img_path"

    # Check for errors after running ExifTool
    if [ $? -ne 0 ]; then
    echo "Error: Failed to update metadata for $img_path"
    fi


  # Increment the counter
  ((counter++))
done

# Print completion message
echo "Processing completed for $((counter-1)) images."

#!/bin/bash

# Define paths
img_json_path="$BKDS_NODEJS_DATA/images/master_image_photos_index.json"
base_img_path="$BKDS_NODEJS_PUBLIC"

# Set the cutoff date (formatted as YYYY-MM-DD)
cutoff_date="2024-11-03"

# Total number of threads
num_threads=10

# Calculate the number of items per split
total_items=$(jq length "$img_json_path")
items_per_split=$(( (total_items + num_threads - 1) / num_threads ))  # Round up

# Split the JSON file into smaller JSON files using jq and output to the current directory
echo "Splitting JSON data into $num_threads smaller files..."
for i in $(seq 0 $((num_threads - 1))); do
  start=$((i * items_per_split))
  end=$((start + items_per_split - 1))
  jq ".[$start:$end]" "$img_json_path" > "./temp_split_${i}.json"
done

# Check if the JSON files were created
if [ ! -f "./temp_split_0.json" ]; then
  echo "Error: Could not create split JSON files."
  exit 1
fi

# Create thread scripts for processing
for i in $(seq 0 $((num_threads - 1))); do
  thread_file="thread$((i + 1)).sh"
  split_file="./temp_split_${i}.json"

  echo "#!/bin/bash" > "$thread_file"
  echo "base_img_path=\"$base_img_path\"" >> "$thread_file"
  echo "img_json_path=\"$split_file\"" >> "$thread_file"
  echo "Processing files in $split_file..." >> "$thread_file"

  cat << 'EOF' >> "$thread_file"
  jq -c '.[]' "$img_json_path" | while read -r image; do
    img_path="$base_img_path$(echo "$image" | jq -r '.img_url' | sed 's/ /_/g')"
    #echo "img_path: $img_path"

    # Check if the file path contains 'youtube' or '_yt_'
    if [[ "$img_path" == *"youtube"* || "$img_path" == *"_yt_"* ]]; then
      echo "Skipping file due to 'youtube' criteria: $img_path"
      continue
    fi

    # Check if the file exists and is older than the cutoff date
    if [ -f "$img_path" ]; then
      file_mod_date=$(date -r "$img_path" +"%Y-%m-%d")
      if [[ "$file_mod_date" > "$cutoff_date" ]]; then
       # echo "Skipping file due to modification date newer than $cutoff_date: $img_path"
        continue
      fi
    else
      echo "File does not exist: $img_path"
      continue
    fi

    img_title=$(echo "$image" | jq -r '.img_title')
    img_desc1=$(echo "$image" | jq -r '.img_desc1')
    img_desc2=$(echo "$image" | jq -r '.img_desc2')
    img_data_category=$(echo "$image" | jq -r '.data_category | .[0:5] | join(" ")' | sed -e 's/ /, /g' -e 's/_/ /g')
    img_data_subject=$(echo "$image" | jq -r '.data_subject | .[0:5] | join(" ")' | sed -e 's/ /, /g' -e 's/_/ /g')

    echo "Processing $img_path"

    exiftool -overwrite_original \
      -Title="$img_title" \
      -Description="$img_desc1 $img_desc2" \
      -Keywords="$img_data_category" \
      -Subject="$img_data_subject" \
      "$img_path"

    echo "Completed processing $img_path"
  done
EOF

  chmod +x "$thread_file"
done

# Run the thread scripts in parallel
echo "Running thread scripts in parallel..."
for i in $(seq 1 $num_threads); do
  ./thread${i}.sh &
done

# Wait for all parallel scripts to complete
wait

# Clean up temporary files
rm temp_split_*.json

# Print completion message
echo "Processing completed for all threads."

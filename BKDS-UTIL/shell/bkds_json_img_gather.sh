#!/bin/bash

# Set the source path (you can change this)
if [ -z "$BKDS_NODEJS_DATA" ]; then
    echo "Error: BKDS_NODEJS_DATA environment variable is not set."
    exit 1
fi

source_path="$BKDS_NODEJS_DATA/content_feeds"  # Using the environment variable

# Function to count occurrences of image filename patterns in JSON files
count_image_patterns() {
  find "$source_path" -name "*.json" -print0 | \
    xargs -0 grep -Eioh '("_PIL_[24710]\S*\.jp[e]*g"|"*_PIL_\S*\.jp[e]*g"|"*_PIL_[24710]\S*\.png"|"*_PIL_\S*\.png")' | \
    sed 's/.*\("_PIL_[24710]\S*\.jp[e]*g"|"*_PIL_\S*\.jp[e]*g"|"*_PIL_[24710]\S*\.png"|"*_PIL_\S*\.png"\).*/\1/' | \  # Extract only the filename
    sort | uniq -c
}

# Count the occurrences and display the report
count_image_patterns 2>/dev/null  # Redirect stderr to /dev/null

# (Optional) Save the report to a file
# count_image_patterns 2>/dev/null > image_pattern_report.txt
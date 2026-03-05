#!/bin/bash

# Define the directory
read -p "Enter the directory path where you want to move .jpeg files: " directory

# Ensure the directory exists
if [[ ! -d "$directory" ]]; then
  echo "The provided path is not a valid directory."
  exit 1
fi

# Create the 'jpeg' folder if it doesn't exist
mkdir -p "$directory/jpeg"

# Move all .jpeg files to the 'jpeg' folder
find "$directory" -maxdepth 1 -type f -name "*.jpeg" -exec mv {} "$directory/jpeg" \;

echo "All .jpeg files have been moved to the 'jpeg' folder."

#!/bin/bash

# Define a function to process and modify a shell script
modify_script() {
    local script="$1"
    echo "Modifying script: $script"
    
    # Use sed to append "&& echo \"$1\"" to matching lines
    sed -i.bak 's|&& echo "$1" && echo "$1" && echo "$1" && echo "$1"&& echo "$1" && echo "$1" && echo "$1" && echo "$1" echo "$1"|&& echo "$1"|' "$script"
}

# Find all shell scripts in the specified directory and its subdirectories
root_directory="$HOME/Documents/Sync/BKDS/BKDS-APP"
find "$root_directory" -type f -name "*.sh" | while read -r script; do
    modify_script "$script"
done

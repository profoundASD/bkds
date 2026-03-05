#!/usr/bin/env bash

########################################
# User-Configurable Variables
########################################

# Location of the config JSON file
SOURCE_JSON="/home/aimless76/Documents/Sync/BKDS/BKDS-APP-DEV/BKDS-UTIL/data/config/bkds_gallery_launch_sources.json"

# File extensions to look for (case-insensitive)
IMAGE_EXTENSIONS="jpg jpeg png"

########################################
# Helper Functions
########################################

check_requirements() {
    if ! command -v jq &> /dev/null; then
        echo "[ERROR] 'jq' not found. Please install jq to continue."
        exit 1
    fi

    if ! command -v gthumb &> /dev/null; then
        echo "[ERROR] 'gthumb' not found. Please install gthumb to launch the gallery."
        exit 1
    fi

    if [ ! -f "$SOURCE_JSON" ]; then
        echo "[ERROR] Source JSON file '$SOURCE_JSON' does not exist."
        exit 1
    fi
}

load_config() {
    echo "[INFO] Loading configuration from '$SOURCE_JSON'..."

    DIRECTORIES=$(jq -c '.directories[]' "$SOURCE_JSON" 2>/dev/null)
    TARGET_DIR=$(jq -r '.target_dir' "$SOURCE_JSON" 2>/dev/null)

    if [ -z "$DIRECTORIES" ]; then
        echo "[ERROR] No directories found in '$SOURCE_JSON' or invalid JSON structure."
        exit 1
    fi

    if [ -z "$TARGET_DIR" ] || [ "$TARGET_DIR" = "null" ]; then
        echo "[ERROR] 'target_dir' not defined or invalid in '$SOURCE_JSON'."
        exit 1
    fi

    # Ensure target directory exists
    if [ ! -d "$TARGET_DIR" ]; then
        echo "[INFO] Target directory '$TARGET_DIR' does not exist. Creating it now..."
        mkdir -p "$TARGET_DIR" || { echo "[ERROR] Could not create target directory '$TARGET_DIR'."; exit 1; }
    fi

    echo "[INFO] Configuration loaded."
    echo "       Directories: $(echo "$DIRECTORIES" | wc -l) directories."
    echo "       Target Dir: $TARGET_DIR"
}

update_last_processed() {
    local dir="$1"
    local timestamp="$2"

    jq --arg dir "$dir" --arg ts "$timestamp" \
       '(.directories[] | select(.path == $dir) | .last_processed) = $ts' \
       "$SOURCE_JSON" > "${SOURCE_JSON}.tmp" && mv "${SOURCE_JSON}.tmp" "$SOURCE_JSON"
}

########################################
# Main Logic
########################################

check_requirements
load_config

# Convert extensions into a case-insensitive find pattern
EXT_PATTERNS=""
for ext in $IMAGE_EXTENSIONS; do
    if [ -z "$EXT_PATTERNS" ]; then
        EXT_PATTERNS="-iname \"*.$ext\""
    else
        EXT_PATTERNS="$EXT_PATTERNS -o -iname \"*.$ext\""
    fi
done

# Process each directory
echo "$DIRECTORIES" | while read -r DIR_INFO; do
    DIR_PATH=$(echo "$DIR_INFO" | jq -r '.path')
    LAST_PROCESSED=$(echo "$DIR_INFO" | jq -r '.last_processed // "1970-01-01T00:00:00"')

    echo "[INFO] Processing directory: $DIR_PATH (last processed: $LAST_PROCESSED)"
    if [ ! -d "$DIR_PATH" ]; then
        echo "[WARN] '$DIR_PATH' is not a directory. Skipping..."
        continue
    fi

    # Find files modified after the last processed time
    FILES=$(eval "find \"$DIR_PATH\" -type f \( $EXT_PATTERNS \) -newermt \"$LAST_PROCESSED\"")
    if [ -z "$FILES" ]; then
        echo "[INFO] No new files found in $DIR_PATH."
        continue
    fi

    echo "[INFO] Found new files in $DIR_PATH. Creating symbolic links in $TARGET_DIR..."
    for FILEPATH in $FILES; do
        FULLPATH="$(readlink -f "$FILEPATH" 2>/dev/null || echo "$FILEPATH")"
        BASENAME=$(basename "$FULLPATH")
        LINK_PATH="$TARGET_DIR/$BASENAME"

        if [ -L "$LINK_PATH" ]; then
            echo "[DEBUG] Link already exists: $LINK_PATH"
            continue
        fi

        echo "[INFO] Creating symbolic link: $LINK_PATH"
        ln -s "$FULLPATH" "$LINK_PATH"
    done

    # Update the last processed timestamp
    CURRENT_TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")
    update_last_processed "$DIR_PATH" "$CURRENT_TIMESTAMP"
done

echo "[INFO] Processing complete. All symbolic links are in '$TARGET_DIR'."

# Launch gthumb with the target directory, sorting by date and reversing order (descending)
echo "[INFO] Launching gthumb with images sorted by date descending..."
killall -9 gthumb
gthumb "$TARGET_DIR" --sort=date --reverse

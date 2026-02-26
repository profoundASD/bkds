#!/usr/bin/env python3

import os
import re
import json
import sys
import argparse
from bkds_Utilities import log_msg

##########################################
# Setup and Global Variables

def logMsg(msg):
    """ Log a message using the logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)  # Optional: Remove if console output is not desired

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process images and JSON files to update file extensions.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
program_name = os.path.basename(__file__)

# Directory containing images and JSON files
nodejs_dir = os.getenv('BKDS_NODEJS_DATA', '.')
start_directory = os.path.join(nodejs_dir, ".")

# Mapping of extensions to replace: {pattern_to_match: replacement}
extension_mapping = {
    '.JPEG': '.jpg',
    '.jpeg': '.jpg'
}

# Counters for logging
file_counters = {
    'files_processed': 0,
    'files_renamed': 0,
    'files_skipped': 0,
    'json_files_processed': 0,
    'json_files_updated': 0,
    'json_files_skipped': 0
}

##########################################
# Main Logic and Functions

def rename_files(start_dir):
    for root, _, files in os.walk(start_dir):
        for file in files:
            original_file = file
            file_counters['files_processed'] += 1
            file_path = os.path.join(root, file)

            # Check if file extension matches any in the mapping
            for old_ext, new_ext in extension_mapping.items():
                if file.lower().endswith(old_ext.lower()):
                    new_file = re.sub(re.escape(old_ext) + '$', new_ext, file, flags=re.IGNORECASE)
                    new_file_path = os.path.join(root, new_file)

                    if os.path.exists(new_file_path):
                        logMsg(f"Skipped renaming (target exists): '{file_path}'")
                        file_counters['files_skipped'] += 1
                    else:
                        os.rename(file_path, new_file_path)
                        logMsg(f"Renamed: '{file_path}' -> '{new_file_path}'")
                        file_counters['files_renamed'] += 1
                    break
            else:
                # No matching extension found
                file_counters['files_skipped'] += 1

def update_json_file(file_path):
    file_counters['json_files_processed'] += 1
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        logMsg(f"Skipping invalid JSON file: {file_path}")
        file_counters['json_files_skipped'] += 1
        return

    updated = False

    def replace_extensions(obj):
        nonlocal updated
        if isinstance(obj, dict):
            return {k: replace_extensions(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_extensions(element) for element in obj]
        elif isinstance(obj, str):
            for old_ext, new_ext in extension_mapping.items():
                pattern = re.escape(old_ext) + '$'
                if re.search(pattern, obj, flags=re.IGNORECASE):
                    new_obj = re.sub(pattern, new_ext, obj, flags=re.IGNORECASE)
                    if new_obj != obj:
                        updated = True
                        logMsg(f"Updated string in JSON from '{obj}' to '{new_obj}'")
                        return new_obj
            return obj
        else:
            return obj

    updated_data = replace_extensions(data)

    if updated:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
        logMsg(f"Updated JSON file: {file_path}")
        file_counters['json_files_updated'] += 1
    else:
        file_counters['json_files_skipped'] += 1

def walk_and_process(start_dir):
    logMsg(f"Starting processing in directory: {start_dir}")
    rename_files(start_dir)
    for root, _, files in os.walk(start_dir):
        for file in files:
            if file.lower().endswith('.json'):
                file_path = os.path.join(root, file)
                update_json_file(file_path)

    # Log summary of operations
    logMsg("Processing completed.")
    logMsg(f"Files processed: {file_counters['files_processed']}")
    logMsg(f"Files renamed: {file_counters['files_renamed']}")
    logMsg(f"Files skipped: {file_counters['files_skipped']}")
    logMsg(f"JSON files processed: {file_counters['json_files_processed']}")
    logMsg(f"JSON files updated: {file_counters['json_files_updated']}")
    logMsg(f"JSON files skipped: {file_counters['json_files_skipped']}")

if __name__ == "__main__":
    walk_and_process(start_directory)

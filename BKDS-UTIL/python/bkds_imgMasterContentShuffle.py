import os
import json
import random
import shutil
import argparse
import zipfile
import time
from pathlib import Path
from datetime import datetime
from bkds_Utilities import log_msg
import socket
# Configuration
out_dir = os.getenv('BKDS_NODEJS_DATA')
DIRECTORY_PATH = os.path.join(out_dir, "images")  # Directory to search for JSON files
ARCHIVE_PATH = './archive'  # Archive directory
ARCHIVE_PATH = os.getenv('BKDS_ARCHIVE', '/default/path/for/util_data')
# Get the hostname of the machine
hostname = socket.gethostname()

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

# Construct the archive path
ARCHIVE_PATH = os.path.join(ARCHIVE_PATH, hostname, current_date)
EXCLUDE_FILES = ["master_image_screenshots.json"]  # List of files to exclude
FILENAME_PATTERN = "master_image"  # Pattern prefix to match JSON files
DAYS_TO_KEEP_ARCHIVE = 3  # Days to retain archives
program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process images into a JSON file based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id

def logMsg(msg):
    """ Log a message to the console and using a logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)

def shuffle_json_file(file_path):
    """Shuffle contents of a JSON file, re-index with data_src_index, and save the shuffled content back."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    random.shuffle(data)  # Shuffle the list of JSON objects

    # Re-index each item after shuffling
    for index, item in enumerate(data):
        item['data_src_index'] = index

    # Save the shuffled and re-indexed data back to the file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def backup_and_shuffle(file_path):
    """Back up the JSON file, shuffle the contents, and save it back."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create a single backup file per index
    backup_file = Path(ARCHIVE_PATH) / f"{file_path.stem}.bak.{timestamp}.json"

    # Copy original file to backup location
    shutil.copy2(file_path, backup_file)

    # Shuffle and save JSON data with minimal lock time
    shuffle_json_file(file_path)

    # Archive the backup
    archive_file = Path(ARCHIVE_PATH) / f"{file_path.stem}.{timestamp}.zip"  # Include timestamp in the archive name
    with zipfile.ZipFile(archive_file, 'w') as zipf:  # Use 'w' mode to overwrite the archive
        zipf.write(backup_file, arcname=backup_file.name)

    # Remove the backup file after archiving
    backup_file.unlink()

def clean_old_archives():
    """Delete archive files older than a specified number of days."""
    cutoff_time = time.time() - DAYS_TO_KEEP_ARCHIVE * 86400  # Convert days to seconds
    for archive_file in Path(ARCHIVE_PATH).glob("*.zip"):
        if archive_file.stat().st_mtime < cutoff_time:
            archive_file.unlink()

def main():
    # Ensure archive directory exists
    os.makedirs(ARCHIVE_PATH, exist_ok=True)

    # Walk through directory and process JSON files
    for file_path in Path(DIRECTORY_PATH).glob("*.json"):
        if file_path.name in EXCLUDE_FILES or not file_path.name.startswith(FILENAME_PATTERN):
            continue  # Skip excluded files and non-matching patterns

        try:
            backup_and_shuffle(file_path)
            print(f"Processed and shuffled {file_path.name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    # Clean up old archives
    clean_old_archives()

if __name__ == "__main__":
    main()

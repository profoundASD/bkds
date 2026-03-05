#!/usr/bin/env python3

"""
Screenshot Indexer

Purpose:
This script indexes image files with the pattern `_SCREENSHOTS_` in the filename,
extracts relevant metadata, and saves this information in a JSON file. It retrieves images
from the last 14 days, and includes the date folder in the endpoint path to serve images directly.

Usage:
    ./screenshot_indexer.py <batch_id>

Environment Variables:
    BKDS_UTIL_DATA        - Base path for utility data
    BKDS_NODEJS_DATA      - Base path for Node.js data
    BKDS_REPORTING_DATA   - Base path for reporting data
"""

import os
import hashlib
import json
from pathlib import Path
import re
import socket
import argparse
from datetime import datetime, timedelta
import zipfile
from bkds_Utilities import log_msg

# Function to retrieve hostname from nodeid.json as a backup
def get_hostname_from_file(file_path, default_hostname='bkds-demo-pc'):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get("preferred_hostname", default_hostname)
    except (FileNotFoundError, json.JSONDecodeError):
        logMsg(f"Error reading hostname from {file_path}, using default: {default_hostname}")
        return default_hostname

# Read environment variables
util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')
reporting_data = os.getenv('BKDS_REPORTING_SCREENSHOTS')
node_id_file = os.path.join(util_data, 'config', 'bkds_node_id.json')
hostname = socket.gethostname() or get_hostname_from_file(node_id_file)
days_to_index = 30

# Define paths and filenames
image_index_dir = 'images'
img_index_filename_prefix = 'master_image_'
index_type = 'screenshots_index'
index_file_type = 'json'
img_index_name = img_index_filename_prefix + index_type + '.' + index_file_type
node_id_file = os.path.join(util_data, 'config', 'bkds_node_id.json')  # Path to node ID file
# Input/output directories
input_base_directory = os.path.join(reporting_data, hostname)
output_json = os.path.join(nodejs_data, image_index_dir, img_index_name)
archive_dir = os.path.join(nodejs_data, image_index_dir, 'archive')
node_id_file = os.path.join(util_data, 'config', 'bkds_node_id.json')  # Path to node ID file

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id

def logMsg(msg):
    log_msg(os.path.basename(__file__), batch_id, msg)
    print(msg)

def calculate_md5(filepath):
    #logMsg(f"calculate_md5() with {filepath}")
    return hashlib.md5(filepath.encode()).hexdigest()

def extract_details_from_filename(filename):
    #logMsg(f"extract_details_from_filename() with {filename}")
    # Normalize the filename
    filename = filename.strip()

    # Check for valid image extension
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        logMsg("Filename does not have a valid image extension, skipping.")
        return None

    # Extract host, date, and time
    try:
        host = filename.split('_BKDS_')[0]  # Extracts the host before _BKDS_
        date_time_match = re.search(r'_(\d{8})_(\d{6})\.', filename)
        date = date_time_match.group(1) if date_time_match else None
        time = date_time_match.group(2) if date_time_match else None

        # Determine screenshot_type based on filename content
        if '_USER_' in filename:
            screenshot_type = "USER GENERATED"
        elif '_AUTO_STEP_' in filename:
            screenshot_type = "AUTOMATION"
        else:
            screenshot_type = "unknown"

        # Description extracted from the filename as a fallback
        description = filename.split('_SCREENSHOTS_')[1] if '_SCREENSHOTS_' in filename else filename

        return {
            'host': host,
            'screenshot_type': screenshot_type,
            'description': description.strip(),
            'date': date,
            'time': time,
        }
    except Exception as e:
        logMsg(f"Error processing filename {filename}: {e}")
        return None


def create_image_entry(file_path, date_folder):
    #logMsg(f"Processing file: {file_path}")

    # Extract filename and details
    filename = file_path.name
    details = extract_details_from_filename(filename)
    if not details:
        logMsg(f"Failed to extract details for {filename}. Skipping.")
        return None

    # Get file metadata
    try:
        file_stats = file_path.stat()
        file_mtime = datetime.fromtimestamp(file_stats.st_mtime)
    except Exception as e:
        logMsg(f"Error accessing file metadata for {file_path}: {e}")
        return None

    # Construct image entry details
    img_url_id = calculate_md5(str(file_path))
    img_url = f'/serve-image?date={date_folder}&file={filename}'
    img_title = filename.split('_SCREENSHOTS_')[0].strip()

    # Create descriptions
    img_desc1 = f"[{details['screenshot_type']}] Screenshot"
    img_desc2 = f"{details['host']} {details['screenshot_type']}_SCREENSHOT"

    # Log the constructed entry details
    #logMsg(f"Generated img_url: {img_url}")
    #logMsg(f"Generated img_desc1: {img_desc1}")
    #logMsg(f"Generated img_desc2: {img_desc2}")

    # Return the image entry dictionary
    return {
        "img_url_id": img_url_id,
        "img_url": img_url,
        "img_title": img_title,
        "img_desc1": img_desc1,
        "img_desc2": img_desc2,
        "label": "screenshot",
        "data_category": [details['screenshot_type']],
        "data_subject": [details['screenshot_type']],
        "date": file_mtime.strftime('%Y%m%d'),
        "time": file_mtime.strftime('%H%M%S')
    }


def get_date_folders(base_directory, days=14):
    logMsg(f"get_date_folders() with {base_directory}")
    date_folders = []
    today = datetime.now().date()
    min_date = today - timedelta(days=days - 1)
    for entry in os.listdir(base_directory):
        full_path = os.path.join(base_directory, entry)
        if os.path.isdir(full_path) and re.match(r'^\d{8}$', entry):
            try:
                folder_date = datetime.strptime(entry, '%Y%m%d').date()
                if min_date <= folder_date <= today:
                    date_folders.append((entry, full_path))
            except ValueError:
                continue
    return date_folders

def index_images(base_directory, days=14):
    logMsg(f"index_images() with {base_directory}")
    image_entries = []
    date_folders = get_date_folders(base_directory, days)
    for date_folder, directory in date_folders:
        for root, _, files in os.walk(directory):
            for file in files:
                if '_SCREENSHOTS_' in file:
                    file_path = Path(root) / file
                    image_entry = create_image_entry(file_path, date_folder)
                    if image_entry:
                        image_entries.append(image_entry)
    return image_entries

def sort_and_mix_images(images):
    logMsg(f"sort_and_mix_images()")
    images.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
    user_screenshots = [img for img in images if img['img_desc1'].startswith("[USER]")]
    automated_screenshots = [img for img in images if img['img_desc1'].startswith("[AUTOMATION]")]
    recent_user_screenshots = user_screenshots[:10]
    remaining_user_screenshots = user_screenshots[10:]
    top_20_images = recent_user_screenshots + automated_screenshots[:20 - len(recent_user_screenshots)]
    top_20_images.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
    mixed_images = top_20_images + automated_screenshots[20:] + remaining_user_screenshots
    return mixed_images

def save_to_json(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    logMsg(f"Data saved to {output_file}")

def archive_existing_file(output_file):
    logMsg(f"archive_existing_file() : {output_file}")
    if os.path.exists(output_file):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_filename = f"{Path(output_file).stem}_{timestamp}.zip"
        archive_path = os.path.join(archive_dir, archive_filename)
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        with zipfile.ZipFile(archive_path, 'w') as archive_zip:
            archive_zip.write(output_file, arcname=Path(output_file).name)
        logMsg(f"Archived existing file to {archive_path}")

def main():
    logMsg(f'Using input_base_directory: {input_base_directory}')
    # Collect and process new image data
    new_image_data = index_images(input_base_directory, days_to_index)
    new_image_data = sort_and_mix_images(new_image_data)

    # Assign data_src_index in sorted order
    for index, image in enumerate(new_image_data):
        image['data_src_index'] = index

    # Check for changes against existing data and save if there are any updates
    if os.path.exists(output_json):
        try:
            with open(output_json, 'r') as f:
                existing_image_data = json.load(f) or []  # Default to empty list if JSON is empty
        except json.JSONDecodeError:  # Handle empty or invalid JSON file
            logMsg(f"Invalid JSON in {output_json}. Defaulting to empty data.")
            existing_image_data = []  # Default to empty list

        if new_image_data != existing_image_data:
            archive_existing_file(output_json)
            save_to_json(new_image_data, output_json)
            logMsg(f"save_to_json saved to: {output_json}")
        else:
            logMsg("No changes detected. Existing file not overwritten.")
    else:
        save_to_json(new_image_data, output_json)
    
    logMsg("Indexing complete")



if __name__ == "__main__":
    main()

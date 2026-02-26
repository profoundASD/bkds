#!/usr/bin/env python3
"""
Script Name: Download Manager
Description:
    This script processes a batch of image URLs from a database, downloading each image based on its source.
    For 'wiki' sources, images are downloaded using the curl command; for others, the requests library is used.
    The script ensures filenames and extensions are in lowercase and standardizes image extensions.
    It also archives invalid images (zero-byte files, text files, or images containing a "not found" string) before loading valid images into the database.

Usage:
    python download_manager.py <query_key> --low <min_sleep_seconds> --high <max_sleep_seconds>

Arguments:
    query_key: Unique identifier for the batch to be processed.
    --low: Minimum number of seconds to sleep randomly after each download.
    --high: Maximum number of seconds to sleep randomly after each download.
"""

import os
import hashlib
import zipfile
import requests
import json
import time
import random
import argparse
import re
import subprocess
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from bkds_Utilities import log_msg, fetch_data, get_sqlTemplate
from bkds_backend_imgCacheGen_DBLoad import loadDB

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("query_key", help="query key")
    parser.add_argument("--low", type=float, default=1, help="Minimum sleep time in seconds")
    parser.add_argument("--high", type=float, default=4, help="Maximum sleep time in seconds")
    return parser.parse_args()

args = parse_arguments()
query_key = args.query_key

# Set environment variables or replace with actual paths
util_data = os.getenv('DEVUTIL')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

content_root = 'image_cache'
output_dir = os.path.join(util_data, content_root)
prefix = 'bkds'
proc_log = f'{prefix}_{program_name}_{query_key}.log'
mapping_file = f'bkds_data_mappings.json'
mapping_env = os.getenv('BKDS_UTIL_DATA')
mapping_dir = os.path.join(mapping_env, 'config', mapping_file)
dup_file = f'{prefix}_{program_name}_{query_key}_duplicates'
archive_folder = 'archive'
thumbnail_dir = 'thumbnail'

########################################################################
# Main logic and functions

def logMsg(msg):
    log_msg(program_name, query_key, msg)
    print(msg)

def build_file_list(directory):
    all_files = set()
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(subdir, file)
            all_files.add(full_path)
    return all_files

def sanitize_filename(filename):
    # Convert filename and extension to lowercase
    filename = filename.lower()
    # Replace .jpeg with .jpg
    filename = re.sub(r'\.jpeg$', '.jpg', filename)
    # Sanitize filename by replacing invalid characters
    filename = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename

def download_with_curl(img_url, file_path):
    cmd = ['curl', '-s', '-o', file_path, img_url]
    subprocess.run(cmd)

def enforce_rest_interval(start_time, interval=300):
    if time.time() - start_time > interval:
        rest_duration = random.randint(600, 1200)  # Random sleep between 10 to 20 minutes
        logMsg(f"Pausing for {rest_duration / 60} minutes to avoid overloading servers.")
        time.sleep(rest_duration)
        return time.time()  # Reset the start time after the rest
    return start_time

def determine_src_type(query_key):
    if "yt" in query_key:
        return 'yt'
    elif "flickr" in query_key:
        return 'flickr'
    elif "wiki" in query_key:
        return 'wiki'
    return 'unknown'

def download_images(image_data, target_folder, src_type, low, high, existing_files):
    start_time = time.time()  # Track when the script starts downloading images
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    log_file_path = os.path.join(target_folder, proc_log)
    with open(log_file_path, 'w') as log_file:
        for entry in image_data:
            start_time = enforce_rest_interval(start_time)  # Check if it needs to rest

            img_url = entry['img_url']
            img_url_id = entry['img_url_id']
            img_type = entry['img_type']
            original_filename = img_url.split('/')[-1]
            hygiened_filename = sanitize_filename(original_filename)
            filename = f"{img_type}_{src_type}_{img_url_id}_{hygiened_filename}"

            dl_folder = os.path.join(target_folder, img_type)
            if not os.path.exists(dl_folder):
                os.makedirs(dl_folder)

            file_path = os.path.join(dl_folder, filename)

            # Skip download if file already exists
            if file_path in existing_files:
                logMsg(f"File already exists, skipping download: {filename}")
                continue

            logMsg(f'Getting: {img_url}')
            try:
                time.sleep(random.uniform(low, high))  # Sleep for a random time interval
                if src_type == 'wiki':
                    download_with_curl(img_url, file_path)
                else:
                    response = requests.get(img_url, stream=True)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        logMsg(f"Downloaded and saved as {filename}")
                    else:
                        log_file.write(f"{img_url} resulted in a {response.status_code} error\n")
                        logMsg(f"Failed to download {img_url}")
            except Exception as e:
                log_file.write(f"{img_url} resulted in an error: {str(e)}\n")
                logMsg(f"Error downloading {img_url}: {str(e)}")

def archive_invalid_images(target_directory):
    invalid_files = []
    archive_dir = os.path.join(target_directory, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, target_directory)

                # Convert filename and extension to lowercase, and .jpeg to .jpg
                new_filename = sanitize_filename(file)
                new_path = os.path.join(root, new_filename)

                if path != new_path:
                    os.rename(path, new_path)
                    path = new_path

                try:
                    # Check if file is zero bytes
                    if os.path.getsize(path) == 0:
                        logMsg(f"Zero-byte file found: {rel_path}")
                        invalid_files.append(path)
                        continue

                    # Try to open the image to check if it's valid
                    with Image.open(path) as img:
                        img.verify()  # Verify that it is, in fact, an image
                except (UnidentifiedImageError, IOError):
                    # The file is not a valid image
                    logMsg(f"Invalid image file (cannot open): {rel_path}")
                    invalid_files.append(path)
                    continue
                except Exception as e:
                    logMsg(f"Error verifying image {rel_path}: {e}")
                    invalid_files.append(path)
                    continue

                # Check if the file contains the string "not found"
                try:
                    with open(path, 'rb') as f:
                        file_content = f.read()
                        if b'not found' in file_content.lower():
                            logMsg(f"File contains 'not found' string: {rel_path}")
                            invalid_files.append(path)
                            continue
                except Exception as e:
                    logMsg(f"Error reading file {rel_path}: {e}")
                    invalid_files.append(path)
                    continue

    if invalid_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(archive_dir, f'invalid_images_{timestamp}.zip')
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for invalid_file in invalid_files:
                arcname = os.path.relpath(invalid_file, target_directory)
                zipf.write(invalid_file, arcname)
                os.remove(invalid_file)  # Remove the invalid file after adding it to the zip
        logMsg(f"Archived invalid images to {archive_path}")

def deduplicate_images(target_directory):
    filename_table = {}
    duplicates = []
    archive_dir = os.path.join(target_directory, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, target_directory)
                if file in filename_table:
                    logMsg(f"Duplicate found: {rel_path}")
                    duplicates.append(path)
                else:
                    filename_table[file] = path

    if duplicates:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(archive_dir, f'duplicates_{timestamp}.zip')
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for dup in duplicates:
                arcname = os.path.relpath(dup, target_directory)
                zipf.write(dup, arcname)
                os.remove(dup)  # Remove the duplicate file after adding it to the zip
        logMsg(f"Archived duplicate images to {archive_path}")

def main():
    logMsg(f"Starting main for {query_key} from {program_name}")

    src_type = determine_src_type(query_key)
    poc_dir = os.path.join(output_dir, src_type)

    existing_files = build_file_list(poc_dir)
    sql_query = get_sqlTemplate(query_key)
    image_data = fetch_data(sql_query)  # Fetch data using the SQL query

    download_images(image_data, poc_dir, src_type, args.low, args.high, existing_files)

    # Archive invalid images before loading to the database
    archive_invalid_images(poc_dir)

    # Deduplicate images
    deduplicate_images(poc_dir)

    # Load valid images into the database
    loadDB(query_key, poc_dir)

if __name__ == '__main__':
    main()

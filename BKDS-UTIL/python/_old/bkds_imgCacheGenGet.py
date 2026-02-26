"""
Script Name: Download Manager
Description:
    This script processes a batch of image URLs from a database, downloading each image based on its source.
    For 'wiki' sources, images are downloaded using the curl command; for others, the requests library is used.
    Every 5 minutes, the script pauses for a random duration between 5 to 10 minutes to avoid overloading servers.
    This script is intended for batch processing of images for data analysis purposes, maintaining a log of all operations.

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
import os
import json
import time
import random
import argparse
import re
import subprocess  # Needed to run curl
from datetime import datetime
from PIL import Image
from bkdsUtilities import log_msg, fetch_data, get_sqlTemplate

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("query_key", help="query key")
    parser.add_argument("src_type", help="source type (yt/wiki/flickr)")
    parser.add_argument("--low", type=float, default=1, help="Minimum sleep time in seconds")
    parser.add_argument("--high", type=float, default=4, help="Maximum sleep time in seconds")
    return parser.parse_args()

args = parse_arguments()
query_key = args.query_key
src_type = args.src_type

# Set environment variables or replace with actual paths
util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

content_root = 'image'
output_dir = os.path.join(nodejs_data, content_root)
prefix='bkds'
#imgCaceGen
query_key = f'{prefix}_{query_key}_{src_type}_select'
proc_log=f'{prefix}_{program_name}_{query_key}.log'
mapping_file = f'bkds_data_mappings.json'
mapping_env = os.getenv('BKDS_UTIL')
mapping_dir = os.path.join(mapping_env, 'sql', mapping_file)
dup_file=f'{prefix}_{program_name}_{query_key}_{src_type}_duplicates'
archive_folder='archive'
thumbnail_dir='pil'
########################################################################
# Main logic and functions
def logMsg(msg):
    log_msg(program_name, query_key, msg)
    print(msg)

# Function to build a list of all files in the directory recursively
def build_file_list(directory):
    all_files = set()  # Use a different name to avoid confusion with the loop variable
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(subdir, file)
            all_files.add(full_path)
    return all_files

def sanitize_filename(filename):
    """Sanitize the filename by removing unsafe characters and replacing spaces with underscores."""
    filename = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename

def download_with_curl(img_url, file_path):
    """Download an image using curl."""
    cmd = ['curl', '-s', '-o', file_path, img_url]
    subprocess.run(cmd)

def enforce_rest_interval(start_time, interval=300):
    """Enforce a rest interval every 5 minutes for a random duration between 5 to 10 minutes."""
    if time.time() - start_time > interval:
        rest_duration = random.randint(10, 30)  # Random sleep between 5 and 10 minutes
        logMsg(f"Pausing for {rest_duration / 60} minutes to avoid overloading servers.")
        time.sleep(rest_duration)
        return time.time()  # Reset the start time after the rest
    return start_time

def download_images(image_data, target_folder, low, high, existing_files):
    start_time = time.time()  # Track when the script starts downloading images
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    log_file_path = os.path.join(target_folder, proc_log)
    with open(log_file_path, 'w') as log_file:
        for entry in image_data:
            start_time = enforce_rest_interval(start_time)  # Check if it needs to rest
            
            img_url = entry['img_url']
            img_url_id = entry['img_url_id']
            data_source = entry['data_source']
            img_type = entry['img_type']
            original_filename = img_url.split('/')[-1]
            hygiened_filename = sanitize_filename(original_filename)
            filename = f"{img_type}_{data_source}_{img_url_id}_{hygiened_filename}"

            dl_folder = os.path.join(target_folder, img_type)
            if not os.path.exists(dl_folder):
                os.makedirs(dl_folder)

            file_path = os.path.join(dl_folder, src_type, filename)
            
            # Skip download if file already exists
            if file_path in existing_files:
                logMsg(f"File already exists, skipping download: {filename}")
                continue

            logMsg(f'getting: {img_url}')
            try:
                time.sleep(random.uniform(low, high))  # Sleep for a random time interval
                if data_source == 'wiki':
                    download_with_curl(img_url, file_path)
                else:
                    response = requests.get(img_url, stream=True)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        logMsg(f"Downloaded and saved as {filename}")
                    else:
                        log_file.write(f"{img_url} resulted in a 404 error\n")
                        logMsg(f"Failed to download {img_url}")
            except Exception as e:
                log_file.write(f"{img_url} resulted in an error: {str(e)}\n")
                logMsg(f"Error downloading {img_url}: {str(e)}")

def deduplicate_images(target_directory):
    # Create a dictionary to track filenames and their paths
    filename_table = {}
    duplicates = []
    
    # Walk through the directory to find all image files
    for root, dirs, files in os.walk(target_directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                path = os.path.join(root, file)
                if file in filename_table:
                    duplicates.append(path)
                else:
                    filename_table[file] = path
    
    # Handle duplicates by moving them to a zip archive
    if duplicates:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(target_directory, f'{archive_folder}/{dup_file}_{timestamp}.zip')
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for dup in duplicates:
                arcname = os.path.basename(dup)
                zipf.write(dup, arcname)
                os.remove(dup)  # Remove the duplicate file after adding it to the zip
        logMsg(f"Duplicates moved to {archive_path}")

def generate_thumbnails(target_directory):
    # Define the sizes for the thumbnails
    sizes = [480, 720, 1080]
    # Create the thumbnail_dir directory if it doesn't exist
    pil_directory = os.path.join(target_directory, thumbnail_dir)
    if not os.path.exists(pil_directory):
        os.makedirs(pil_directory)
    
    # Walk through the directory, find all images, and generate thumbnails
    for root, dirs, files in os.walk(target_directory):
        # Remove the thumbnail_dir directory from dirs to avoid processing it
        if thumbnail_dir in dirs:
            dirs.remove(thumbnail_dir)
        
        for file in files:
            # Check if the file is an image
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(root, file)
                try:
                    # Extract key fields from the filename
                    file_name, file_ext = os.path.splitext(file)
                    parts = file_name.split('_')
                    if len(parts) < 3:
                        continue
                    img_url_id = parts[-1]

                    # Check and generate thumbnails if they do not exist
                    for size in sizes:
                        new_file_name = f"{file_name}_PIL_{size}{file_ext}"
                        new_file_path = os.path.join(pil_directory, new_file_name)
                        
                        if not os.path.exists(new_file_path):
                            # Open the image
                            with Image.open(image_path) as img:
                                # Create a new image for each size
                                img_copy = img.copy()
                                img_copy.thumbnail((size, size), Image.LANCZOS)
                                # Save the thumbnail
                                img_copy.save(new_file_path)
                                logMsg(f"Thumbnail created: {new_file_path}")
                        else:
                            #logMsg(f"Thumbnail already exists: {new_file_path}")
                            continue

                except Exception as e:
                    logMsg(f"Failed to create thumbnail for {image_path}: {e}")

# Example usage
# generate_thumbnails('/path/to/your/target_directory')
def main():
    logMsg(f"starting main for {query_key} from {program_name}")
    existing_files = build_file_list(output_dir)
    sql_query = get_sqlTemplate(query_key)
    image_data = fetch_data(sql_query)  # Fetch data using the SQL query
    download_images(image_data, output_dir, args.low, args.high, existing_files)
    
    deduplicate_images(output_dir)
    generate_thumbnails(output_dir)
    deduplicate_images(output_dir)    #unlikely any duplicates were introduced during thumbnail generation

if __name__ == '__main__':
    main()

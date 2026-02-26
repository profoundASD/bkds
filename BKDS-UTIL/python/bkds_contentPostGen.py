import os
import re
import json
import time
import ujson
import zipfile
import argparse
from datetime import datetime
import time
from bkds_Utilities import log_msg, fetch_data, get_sqlTemplate, split_text_into_spans

"""
BKDS Content Processor

Purpose:
    This script processes insights and related media content into JSON files, organizing the data
    for efficient retrieval and display. It handles image and video metadata, generates structured 
    JSON output, and archives older versions of files.

Logical Flow:
    1. **Argument Parsing**: Accepts a batch ID and optional generation type ('all', 'details', or 'sample').
    2. **Data Transformation**: Processes insights data into a structured format by:
       - Extracting and categorizing images, videos, and metadata.
       - Splitting text content into manageable spans.
       - Associating related topics and default media items.
    3. **Output Generation**: Saves processed data as minimized JSON files while archiving older versions
       for backup.
    4. **Media Handling**: Resolves URLs for media content, ensuring compatibility with local paths or 
       predefined mappings.
    5. **Error Handling**: Captures and logs issues in data transformation, file writing, and archiving.

Usage:
    python bkds_content_processor.py <batch_id> [--gen_type {all,details,sample}]

    - `batch_id`: Unique identifier for the batch processing session.
    - `--gen_type`: Specifies the type of output to generate:
        - 'all' (default): Generates all data types.
        - 'details': Generates detailed JSON output.
        - 'sample': Generates a random sample of the data.

Example:
    python bkds_content_processor.py example_batch123 --gen_type details

Prerequisites:
    - Environment variables `BKDS_NODEJS_DATA` and `BKDS_NODEJS_UTIL_DATA` must be set.
    - Ensure the `bkds_Utilities` module is installed and accessible in the runtime environment.
    - Input data must conform to the expected structure, including image and video metadata.

"""

######################################################################
# Configuration Constants and Defaults
######################################################################
program_name = os.path.basename(__file__)

# String constants
TEXT_BLOCK = 'text_block'
CONTENT_NAME = 'data_category'
DEFAULT_CONTENT_NAME = CONTENT_NAME
MAIN_FEED = 'main_feed'
ARCHIVE = 'archive'
CONTENT = 'content'
RAW = 'raw'
RELATED_TOPICS_KEY = 'related_topics'
INSIGHT_DETAILS = 'insight_details'
MEDIA = 'media'
IMAGES = 'images'
VIDEOS = 'videos'
LABEL = 'label'
DEFAULT_CLUSTER='default_cluster'

# Configuration Constants and Defaults
program_name = os.path.basename(__file__)

# Main Setup / Variables
out_dir = os.getenv('BKDS_NODEJS_DATA')
util_dir = os.getenv('BKDS_NODEJS_DATA')
data_type = 'config'
archive_folder = ARCHIVE
#archive_folder_path = os.path.join(util_dir, data_type, archive_folder)
input_type = 'json'
target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

# Environment variables
OUT_DIR = os.getenv('BKDS_NODEJS_DATA')
UTIL_DIR = os.getenv('BKDS_NODEJS_DATA')

# Paths
PRODUCTION_BASE_PATH = "/data/images/full_size/"
TARGET_ROOT = "./public/data"
CONTENT_ROOT = CONTENT
CONTENT_DIR = os.path.join(TARGET_ROOT, CONTENT_ROOT)
ARCHIVE_FOLDER = ARCHIVE
ARCHIVE_FOLDER_PATH = os.path.join(util_dir, data_type, archive_folder)

# Query and data keys
INSIGHT_QUERY_KEY = 'bkds_contentGen_web_feed_master'
DATA_CATEGORY = 'data_category'
DATA_CATEGORY_ID='data_category_id'
DATA_SUBJECT = 'data_subject'
SUBJECT_CONTENT = 'subject_content'
FEATURED_IMAGES = 'featured_images'
GALLERY_IMAGES = 'images'
VIDEOS = 'videos'
DEFAULT_IMG = 'default_img'
PAGE_URL = 'page_url'
RELATED_TOPICS = RELATED_TOPICS_KEY

# Image and video keys
IMG_URL_ID = 'img_url_id'
IMG_URL = 'img_url'
IMG_TITLE = 'img_title'
IMG_DESC1 = 'imgDesc1'
IMG_DESC2 = 'img_desc2'
IMG_SRC = 'img_src'
VID_URL_ID = 'vid_url_id'
VID_URL = 'vid_url'
VID_TITLE = 'vid_title'
VID_THUMB_URL = 'vid_thumb_url'
URL_ID = 'url_id'
SUBJECT_TITLE = 'subject_title'
CLUSTER_ID = 'cluster_id'

# Output configuration
OUTPUT_TYPE = 'json'
OUTPUT_PREFIX = 'bkds_'
SUBJECT_TYPE = 'contentPostGen'

PROD_BASE_PATH='/home/jason/BKDS-APP/'
DEV_BASE_PATH= '/home/aimless76/Documents/Sync/BKDS/BKDS-APP/'

# Label and metadata keys
LABEL_GALLERY = 'gallery'
LABEL_FEATURED = 'featured'

# URL patterns
URL_PATTERNS = {
    '_yt_': 'youtube',
    '_youtube_': 'youtube',
    '_flickr_': 'flickr',
    '_wiki_': 'wiki'
}

# Date and timestamp formats
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
HARD_CODED_DEFAULT_IMG = "/data/img/bkds_desktop_rockets.png"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process insights and related media content into JSON files based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    parser.add_argument("--gen_type", choices=['all', 'details', 'sample'], default='all', help="Type of output file to generate: 'details' for detailed data, 'sample' for random samples, 'all' for both.")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
gen_type = args.gen_type
output_type = 'json'
output_prefix = 'bkds_' 
subjType = 'contentPostGen'
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

######################################################################
# Utility Functions
######################################################################

def logMsg(msg):
    """ Log a message to the console and using a logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)

def safely_parse_json(json_data):
    if isinstance(json_data, str):
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            logMsg("Failed to decode JSON data.")
            return []
    return json_data

def case_insensitive_exists(local_path):
    directory, file_name = os.path.split(local_path)
    if not os.path.isdir(directory):
        return False  # Directory does not exist
    
    # Check for a matching file in the directory
    return file_name.lower() in (f.lower() for f in os.listdir(directory))


######################################################################
# Main logic and functions
######################################################################

import requests

def verify_images(images, batch_id):
    """
    Verify the existence of image files on disk or their availability on the web.
    Rename files on disk with uppercase extensions to lowercase.

    Args:
        images (list): List of image dictionaries to verify.
        batch_id (str): Batch ID for logging and archiving.

    Returns:
        list: Verified and processed images.
    """
    verified_images = []
    filtered_out_images = []

    # Retrieve the environment variable
    bkds_nodejs_public = os.getenv('BKDS_NODEJS_PUBLIC')
    if not bkds_nodejs_public:
        logMsg("Environment variable BKDS_NODEJS_PUBLIC is not set.")
        return []

    directory_cache = {}  # Cache directory listings and mappings

    for img in images:
        original_url = img[IMG_URL]

        # Check file extension validity
        if not re.search(r'\.(jpg|png|gif|jpeg)$', original_url, re.IGNORECASE):
            logMsg(f"Invalid extension for image: {original_url}")
            filtered_out_images.append(original_url)
            continue

        # Construct full local file path
        local_path = os.path.join(bkds_nodejs_public, original_url.lstrip('/'))

        # Check for HTTP URL
        if original_url.startswith(('http://', 'https://')):
            try:
                response = requests.head(original_url, timeout=5)
                if response.status_code == 200:
                    img[IMG_URL] = process_url(original_url)  # Apply process_url after verification
                    verified_images.append(img)
                else:
                    filtered_out_images.append(original_url)
            except requests.RequestException as e:
                logMsg(f"HTTP image check failed ({e}): {original_url}")
                filtered_out_images.append(original_url)
            continue

        # Check for local file existence using a case-insensitive check
        directory, file_name = os.path.split(local_path)
        if not os.path.isdir(directory):
            logMsg(f"Directory does not exist: {directory}")
            filtered_out_images.append(original_url)
            continue

        # Use cached directory data if available
        if directory in directory_cache:
            dir_data = directory_cache[directory]
        else:
            # Cache the directory listing once and pre-process
            dir_files = os.listdir(directory)
            file_map = {f.lower(): f for f in dir_files}  # Map lowercase names to actual names

            # Build a base name to files mapping for acceptable extensions
            base_file_map = {}
            for f in dir_files:
                f_base, f_ext = os.path.splitext(f)
                f_ext_lower = f_ext.lower()
                if f_ext_lower in {'.jpg', '.jpeg', '.png', '.gif'}:
                    base_file_map.setdefault(f_base.lower(), []).append(f)

            dir_data = {
                'file_map': file_map,
                'base_file_map': base_file_map,
            }
            directory_cache[directory] = dir_data

        file_map = dir_data['file_map']
        base_file_map = dir_data['base_file_map']

        # Step 1: Check for an exact match (case-insensitive)
        matched_file = file_map.get(file_name.lower())
        if matched_file:
            actual_path = os.path.join(directory, matched_file)
            # Rename file to match the expected case if needed
            if matched_file != file_name or not file_name.split('.')[-1].islower():
                base_name, ext = os.path.splitext(file_name)
                new_file_name = f"{base_name}{ext.lower()}"  # Ensure lowercase extension
                new_path = os.path.join(directory, new_file_name)

                # Check if a file with the lowercase extension already exists
                if not os.path.exists(new_path):
                    os.rename(actual_path, new_path)
                    logMsg(f"Renamed file: {actual_path} -> {new_path}")
                    local_path = new_path  # Update local_path to reflect the renamed file
                else:
                    local_path = new_path  # File already exists with lowercase extension
            else:
                local_path = actual_path  # Update local_path to the actual file
        else:
            # Step 2: Attempt to find an equivalent file with a different extension
            base_name, _ = os.path.splitext(file_name)
            matched_files = base_file_map.get(base_name.lower())
            if matched_files:
                # Use the first matching file
                actual_path = os.path.join(directory, matched_files[0])
                logMsg(f"Equivalent file found: {actual_path}")
                local_path = actual_path  # Use the equivalent file
            else:
                # No equivalent file found
                logMsg(f"Local image does not exist: {local_path}")
                filtered_out_images.append(original_url)
                continue

        # If the file exists after renaming or matching, process it
        if os.path.exists(local_path):
            img[IMG_URL] = process_url(local_path)  # Apply process_url after verification
            verified_images.append(img)
        else:
            logMsg(f"Local image does not exist after renaming attempt: {local_path}")
            filtered_out_images.append(original_url)

    # Optionally log filtered-out images
    #if filtered_out_images:
        #log_filtered_out_images(filtered_out_images, batch_id)

    return verified_images

def log_filtered_out_images(filtered_out_images, batch_id):
    """Log the filtered out images to a file."""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    filtered_out_file = os.path.join(ARCHIVE_FOLDER_PATH, f"filtered_out_images_{batch_id}_{timestamp}.txt")
    os.makedirs(ARCHIVE_FOLDER_PATH, exist_ok=True)
    with open(filtered_out_file, 'w') as f:
        for image in filtered_out_images:
            f.write(f"{image}\n")
    logMsg(f"Filtered out images saved to: {filtered_out_file}")


def process_images(gallery_images, featured_images, data_subject, data_category, batch_id):
    """
    Process and verify gallery and featured images, ensuring the list is deduplicated.

    Args:
        gallery_images (list): Gallery images.
        featured_images (list): Featured images.
        data_subject (str): Subject data.
        data_category (str): Category data.
        batch_id (str): Batch ID for logging and archiving.

    Returns:
        list: Verified and deduplicated images.
    """
    images_dict = {}

    # Add gallery images
    for img in gallery_images:
        images_dict[img[IMG_URL_ID]] = {
            IMG_URL_ID: img[IMG_URL_ID],
            IMG_URL: process_url(img[IMG_URL]),  # Replace base path
            IMG_TITLE: img[IMG_TITLE],
            IMG_SRC: img[IMG_SRC],
            IMG_DESC1: img[IMG_TITLE],
            DATA_CATEGORY: data_category,
            DATA_SUBJECT: data_subject,
            LABEL: LABEL_GALLERY
        }

    # Add or update featured images
    for img in featured_images:
        images_dict[img[IMG_URL_ID]] = {
            IMG_URL_ID: img[IMG_URL_ID],
            IMG_URL: process_url(img[IMG_URL]),  # Replace base path
            IMG_TITLE: img[IMG_TITLE],
            IMG_SRC: img[IMG_SRC],
            IMG_DESC1: img[IMG_TITLE],
            DATA_CATEGORY: data_category,
            DATA_SUBJECT: data_subject,
            LABEL: LABEL_FEATURED
        }

    # Convert the dictionary back to a list
    deduplicated_images = list(images_dict.values())

    # Verify and process images
    #return deduplicated_images
    return verify_images(deduplicated_images, batch_id)


def select_default_image(default_image_url, gallery_images, featured_images, media_images, batch_id):
    #logMsg('select_default_image()')
    # Validate provided default image URL
    if default_image_url and os.path.exists(default_image_url):
        return process_url(default_image_url)

    # Helper function to find the first valid 'wiki' image
    def find_first_wiki_image(images):
        for img in images:
            if img.get(IMG_SRC) == 'wiki' and os.path.exists(img.get(IMG_URL)):
                return process_url(img[IMG_URL])  # Process URL directly

    # Search for the first 'wiki' image
    for images in [gallery_images, featured_images, media_images]:
        wiki_image = find_first_wiki_image(images)
        if wiki_image:
            return wiki_image

    # Fallback to the hardcoded default image
    return process_url(HARD_CODED_DEFAULT_IMG)



def process_videos(video_list):
    #logMsg('process_videos()')
    processed_videos = {}
    for video in video_list:
        vid_id = video[VID_URL_ID]
        if vid_id not in processed_videos:
            processed_videos[vid_id] = {
                VID_URL_ID: vid_id,
                VID_URL: process_url(video[VID_URL]),
                VID_TITLE: video[VID_TITLE],
                VID_THUMB_URL: process_url(video[VID_THUMB_URL]),
                LABEL: LABEL_GALLERY
            }
    return list(processed_videos.values())

def process_url(url):
    """
    Process URLs or map local paths based on predefined patterns for production.

    Args:
        url (str): Original image URL.

    Returns:
        str: Mapped production-ready path or URL.
    """
    #logMsg(f"Processing URL: {url}")

    # Regular expression to validate a complete URL
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    # If the URL is valid (web URL), return it as is
    if re.match(url_regex, url):
        return url

    # Map local file paths
    file_name = os.path.basename(url)
    for pattern, folder in URL_PATTERNS.items():
        if pattern in url:
            mapped_path = os.path.join(PRODUCTION_BASE_PATH, folder, file_name)
            #logMsg(f"Mapped local path: {mapped_path}")
            return mapped_path

    # Default fallback for unmapped paths
    fallback_path = os.path.join(PRODUCTION_BASE_PATH, file_name)
    #logMsg(f"Default mapped path: {fallback_path}")
    return fallback_path


def transform_data(insights):
    """
    Transform data with image verification and default image selection.

    Args:
        insights (list): Insights data.

    Returns:
        dict: Transformed data.
    """
    logMsg(f"Starting transform_data @ {datetime.now()}")
    transformed_data = {}

    for record in insights:
       # logMsg(f"handling: reocrd {record}")
        data_category = record.get(DATA_CATEGORY, '')
        data_subject = record.get(DATA_SUBJECT, '')
        content = record.get(SUBJECT_CONTENT, '')
        data_category_id = record.get(DATA_CATEGORY_ID, '')

        # Process text content
        processed_content = split_text_into_spans(content)

        # Build insight details
        insight_details = {
            DATA_CATEGORY: data_category,
            DATA_CATEGORY_ID: data_category_id,
            DATA_SUBJECT: data_subject,
            URL_ID: record.get(URL_ID, ''),
            PAGE_URL: record.get(PAGE_URL, ''),
            SUBJECT_TITLE: record.get(SUBJECT_TITLE, ''),
            CLUSTER_ID: record.get(CLUSTER_ID, DEFAULT_CLUSTER)
        }

        # Process and verify images
        gallery_images = safely_parse_json(record.get(GALLERY_IMAGES, '[]'))
        featured_images = safely_parse_json(record.get(FEATURED_IMAGES, '[]'))
        media_images = process_images(gallery_images, featured_images, data_subject, data_category, batch_id)

        # Select default image
        default_image_url = select_default_image(
            record.get(DEFAULT_IMG, ''),
            gallery_images,
            featured_images,
            media_images,
            batch_id
        )

        # Process videos
        media_videos = process_videos(record.get(VIDEOS, '[]'))

        # Build transformed record
        if data_category not in transformed_data:
            transformed_data[data_category] = {}
        transformed_data[data_category][record.get(URL_ID, '')] = {
            INSIGHT_DETAILS: insight_details,
            TEXT_BLOCK: {CONTENT: processed_content},
            MEDIA: {
                IMAGES: media_images,
                VIDEOS: media_videos,
                DEFAULT_IMG: default_image_url
            },
            RELATED_TOPICS: safely_parse_json(record.get(RELATED_TOPICS, '[]'))
        }

    logMsg(f"Completed transform_data @ {datetime.now()}")
    return transformed_data


def save_to_json(transformed_data, out_dir):
    logMsg("Starting save_to_json")

    for category, items in transformed_data.items():
        logMsg(f"Saving: {category}")
        category_output_dir = os.path.join(out_dir, content_root, category)
        os.makedirs(category_output_dir, exist_ok=True)
        archive_dir = os.path.join(category_output_dir, ARCHIVE)
        os.makedirs(archive_dir, exist_ok=True)
        #logMsg(f"Created directory {category_output_dir}")

        for url_id, item in items.items():
            logMsg(f"Saving: {url_id}")
            content_name = item[INSIGHT_DETAILS].get(CONTENT_NAME, DEFAULT_CONTENT_NAME)
            cluster_id = item[INSIGHT_DETAILS].get(CLUSTER_ID, DEFAULT_CLUSTER)

            # Determine the output path for each URL_ID based on content_name and cluster_id
            if content_name == 'main_feed':
                logMsg(f" content_name main_feed: {content_name}")
                subject_output_path = os.path.join(category_output_dir, f"bkds_main_feed.json")
            else:
                logMsg(f"NOT MAIN FEED os.path.join(category_output_dir, cluster_id, url_id):\n {os.path.join(category_output_dir, cluster_id, url_id)}")
                content_dir = os.path.join(category_output_dir, cluster_id, url_id)
                os.makedirs(content_dir, exist_ok=True)
                subject_output_path = os.path.join(content_dir, f"{url_id}_{content_name}.json")

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            raw_output_path = os.path.join(content_dir, f"{url_id}_{content_name}_raw_{timestamp}.json")
            archive_path = os.path.join(archive_dir, f"{url_id}_{content_name}_{timestamp}.zip")

            try:
                logMsg(f"minimizing: {raw_output_path}")
                # Write minimized JSON data directly
                with open(raw_output_path, 'w') as f:
                    ujson.dump([item], f)  # Save directly as minimized JSON

                #logMsg(f"Raw JSON file for {url_id} in content {content_name} saved successfully at {raw_output_path}")

                # Read the raw JSON data using ujson
                with open(raw_output_path, 'r') as f:
                    raw_json_data = ujson.load(f)

                # Minify the JSON data without extra spaces or line breaks
                minimized_json = ujson.dumps(raw_json_data)

                # Compare with existing file content if it exists
                logMsg(f"checking existence: {subject_output_path}")
                if os.path.exists(subject_output_path):
                    with open(subject_output_path, 'r') as f:
                        existing_data = ujson.load(f)

                    # Serialize both datasets for comparison
                    existing_data_serialized = ujson.dumps(existing_data)
                    new_data_serialized = minimized_json

                    # Compare the existing data with the new data
                    if existing_data_serialized == new_data_serialized:
                        #logMsg(f"No changes detected for {subject_output_path}. Skipping write.")
                        os.remove(raw_output_path)  # Clean up raw file
                        continue

                    timestamped_output_path = f"{subject_output_path}_{timestamp}"
                    os.rename(subject_output_path, timestamped_output_path)
                    #logMsg(f"Renamed existing JSON file to {timestamped_output_path}")

                    with zipfile.ZipFile(archive_path, 'w') as archive:
                        archive.write(raw_output_path, os.path.basename(raw_output_path))
                        archive.write(timestamped_output_path, os.path.basename(timestamped_output_path))
                        #logMsg(f"Archive created successfully at {archive_path}")

                    # Delete the previous batch file after archiving
                    os.remove(timestamped_output_path)
                    #logMsg(f"Deleted previous batch file after archiving")
                else:
                    with zipfile.ZipFile(archive_path, 'w') as archive:
                        archive.write(raw_output_path, os.path.basename(raw_output_path))
                        #logMsg(f"Archive created successfully at {archive_path}")
                
                logMsg(f"finished checking existence: {subject_output_path}")

                # Write the minified JSON data
                with open(subject_output_path, 'w') as f:
                    f.write(minimized_json)

                #logMsg(f"JSON file for {url_id} in content {content_name} saved successfully at {subject_output_path}")

                # Delete the raw file after archiving
                os.remove(raw_output_path)
                #logMsg(f"Deleted raw batch file after archiving")

            except Exception as e:
                logMsg(f"Failed to save JSON file for {url_id} at {subject_output_path}: {e}")


def main():
    """ Main execution function. """
    logMsg(f"Starting main @ {datetime.now()}")

    insights = fetch_data(get_sqlTemplate(INSIGHT_QUERY_KEY))
    category_data = transform_data(insights)
    save_to_json(category_data, out_dir)
    
    logMsg("Script execution completed.")

if __name__ == "__main__":
    main()

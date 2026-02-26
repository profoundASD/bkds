import re
import os
import json
import shutil
import argparse
import urllib.parse
import zipfile

from datetime import datetime
import time
import random
from bkdsUtilities import log_msg, fetch_data, subjGenOutputHandler, get_sqlTemplate

"""
This script processes and combines data from multiple database queries into JSON files.
Each JSON file contains insights along with associated videos, images, and text content, aggregated by data_category.
The data is grouped by `data_category` and saved into files based on the structured data retrieved from a PostgreSQL database.
The program uses batch processing for handling large datasets and logs essential information for debugging and monitoring.

Author: [Your Name]
Date: [Last Updated Date]
Usage: Run the script with a batch ID to process specific subjects.
Example: python [script_name].py <batch_id>
"""
#####################################################################
# Main Setup / Variables
out_dir = os.getenv('BKDS_NODEJS_DATA')
util_dir = os.getenv('BKDS_NODEJS_DATA')
data_type = 'config'
archive_folder = 'archive'
archive_folder_path = os.path.join(util_dir, data_type, archive_folder)
input_type = 'json'
index_file_name = 'bkds_category_index' + '.' + input_type
print(f'index_file_name {index_file_name}')
index_base_path = os.path.join(util_dir, data_type)
index_file_path = os.path.join(index_base_path, index_file_name)
print(f'util_dir {util_dir}')
target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process insights and related media content into JSON files based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    parser.add_argument("--gen_type", choices=['all', 'details', 'sample'], default='all',
                        help="Type of output file to generate: 'details' for detailed data, 'sample' for random samples, 'all' for both.")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
gen_type = args.gen_type
program_name = os.path.basename(__file__)
insight_query_key = 'bkds_contentGen_web_feed_master'
output_type = 'json'
output_prefix = 'bkds_'
subjType = 'contentPostGen'
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
master_index = 'bkds_master_index.json'
########################################################################
# Main logic and functions

def logMsg(msg):
    """ Log a message to the console and using a logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)

def extract_url_title(url):
    logMsg(f"Starting extract_url_title @ {datetime.now()} with {url}")
    """Extract and format the title from a URL."""
    if not url:  # Check if the URL is None or empty
        return "No title found"
    
    try:
        url_path = urllib.parse.urlparse(url).path
        # Extract the last part of the path and replace underscores with spaces
        title = url_path.split('/')[-1].replace('_', ' ')
        return title if title else "No title found"
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        return "Invalid URL format"

def transform_data(insights):
    logMsg(f"Starting transform_data @ {datetime.now()}")
    transformed_data = {}
    for record in insights:
        # Unpack each field from the record dictionary
        cluster_id = record.get('cluster_id', '')
        url_id = record.get('url_id', '')
        subject_id = record.get('subject_id', '')
        data_category = record.get('data_category', '')
        data_category_id = record.get('data_category_id', '')
        data_subject = record.get('data_subject', '')
        data_subject_id = record.get('data_subject_id', 'NO ID')
        subject_title = record.get('subject_title', '')
        page_url = record.get('page_url', '')
        featured_image_id = record.get('featured_image_id', '')
        subject_content = record.get('subject_content', '')

        print(f'url_id {url_id}')
        print(f'cluster_id {cluster_id}')
        print(f'subject_id {subject_id}')
        print(f'data_subject_id {data_subject_id}')
        print(f'data_category_id {data_category_id}')
        # Process JSON fields; ensure correct parsing or fallback to empty lists/dicts
        images = safely_parse_json(record.get('images', '[]'))
        featured_images = safely_parse_json(record.get('featured_images', '[]'))
        videos = safely_parse_json(record.get('videos', '[]'))
        related_topics = safely_parse_json(record.get('related_topics', '[]'))

        # Determine the default image based on availability
        default_img = next((item.get('img_url', '') for item in featured_images if item.get('img_url', '')), 
                           next((item.get('img_url', '') for item in images if item.get('img_url', '')), ''))

        # Extract image IDs for a more compact representation
        image_ids = [img['img_url_id'] for img in images]
        featured_image_ids = [img['img_url_id'] for img in featured_images]

        # Ensure data categories are properly initialized
        if data_category not in transformed_data:
            transformed_data[data_category] = {}

        # Build the data structure
        transformed_data[data_category][url_id] = {
            "insight_details": {
                "url_id": url_id,
                "cluster_id": cluster_id,
                "subject_id": subject_id,
                "subject_title": subject_title,
                "data_category": data_category,
                "data_category_id": data_category_id,
                "data_subject": data_subject,
                "data_subject_id": data_subject_id
            },
            "text_block": {
                "source": page_url,
                "content": subject_content,
                "description": "Overview of " + subject_title
            },
            "media": {
                "videos": videos,
                "feat_gallery_img_ids": featured_image_ids,
                "default_img": default_img if default_img else featured_image_id,
                "gallery_img_ids": image_ids
            },
            "related_topics": related_topics
        }
    return transformed_data

def safely_parse_json(json_data):
    if isinstance(json_data, str):
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            logMsg("Failed to decode JSON data.")
            return []
    else:
        # If json_data is already a dict or list (parsed by the DB driver), just return it
        return json_data

def replace_local_path_with_target(local_path):
    """ Replace local path with a target path root for indexing purposes. """
    filename = os.path.basename(local_path)
    return os.path.join(content_dir, filename)

def generate_unified_index(base_dir, content_root):
    logMsg("Starting to generate unified index")
    index_file_path = os.path.join(base_dir, 'index', master_index)
    os.makedirs(os.path.dirname(index_file_path), exist_ok=True)
    
    index_data = {}
    content_root_path = os.path.join(base_dir, content_root)

    # Recursively walk through the content_root directory
    for root, dirs, files in os.walk(content_root_path):
        for file in files:
            if file.endswith('.json'):  # Assuming we only want to index JSON files
                full_path = os.path.join(root, file)
                transformed_path = replace_local_path_with_target(full_path)
                
                # Extracting key from the filename which should be of the format '[data_subject]_[data_category]_[cluster_id].json'
                file_key = os.path.splitext(file)[0]  # Removes the .json extension
                index_data[file_key] = transformed_path

    archive_index(index_file_path)
    # Write the comprehensive index to a file
    with open(index_file_path, 'w') as index_file:
        json.dump(index_data, index_file, indent=4)
    logMsg(f"Unified index generated successfully at {index_file_path}")

def save_to_json(transformed_data, out_dir):
    logMsg("Starting save_to_json")
    index_updates = {}

    # Iterate through each category in the transformed data
    for category, items in transformed_data.items():
        # Define the category-specific output directory
        category_output_dir = os.path.join(out_dir, content_root, category)
        os.makedirs(category_output_dir, exist_ok=True)
        logMsg(f"Created directory {category_output_dir}")

        data_categories = {}
        for item_id, item in items.items():
            data_category = item.get('insight_details', {}).get('data_category', 'default_category')
            cluster_id = item.get('insight_details', {}).get('cluster_id', 'default_cluster')
            data_subject = item.get('insight_details', {}).get('data_subject', 'default_subject')

            if data_category not in data_categories:
                data_categories[data_category] = {}
            if cluster_id not in data_categories[data_category]:
                data_categories[data_category][cluster_id] = []
            data_categories[data_category][cluster_id].append(item)
            logMsg(f"Item {item_id} for category {category}, data category {data_category}, and data subject {cluster_id} prepared for saving.")

        for data_category, subjects in data_categories.items():
            category_subject_dir = category_output_dir
            for cluster_id, items in subjects.items():
                subject_output_path = os.path.join(category_subject_dir, f"{cluster_id}_{data_category}_{data_subject}.json")
                try:
                    os.makedirs(os.path.dirname(subject_output_path), exist_ok=True)
                    with open(subject_output_path, 'w') as f:
                        json.dump(items, f, indent=4)
                    logMsg(f"JSON file for category {category}, data category {data_category}, and data subject {cluster_id} saved successfully at {subject_output_path}")
                    transformed_path = replace_local_path_with_target(subject_output_path)
                    
                    if category not in index_updates:
                        index_updates[category] = {}
                    index_updates[category][cluster_id] = transformed_path
                except Exception as e:
                    logMsg(f"Failed to save JSON file for data subject {cluster_id} at {subject_output_path}: {e}")

    generate_unified_index(out_dir, content_root)

def update_index(category, subject_index_data, out_dir):
    index_dir = os.path.join(out_dir, 'index')
    os.makedirs(index_dir, exist_ok=True)
    index_file_path = os.path.join(index_dir, f"{category}_index.json")
    logMsg(f"Updating index for {index_file_path}")
    if os.path.exists(index_file_path):
        with open(index_file_path, 'r') as index_file:
            index_data = json.load(index_file)
    else:
        index_data = {}
    index_data.update(subject_index_data)
    with open(index_file_path, 'w') as index_file:
        json.dump(index_data, index_file, indent=4)

def archive_index(index_file_path):
    logMsg(f"Starting archive_index @ {datetime.now()} for {index_file_path}")
    
    # Determine the archive directory based on the index file path
    archive_dir = os.path.join(os.path.dirname(index_file_path), 'archive')
    
    # Create the archive directory if it does not exist
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        logMsg(f"Created archive directory at {archive_dir}")
    
    # Archive the existing index file with a timestamp if it exists
    if os.path.exists(index_file_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archived_file_name = os.path.basename(index_file_path).replace('.json', f'_{timestamp}.json')
        archived_file_path = os.path.join(archive_dir, archived_file_name)
        shutil.move(index_file_path, archived_file_path)
        logMsg(f"Archived index file to {archived_file_path}")

def main():
    """ Main execution function. """
    logMsg(f"Starting main @ {datetime.now()}")
    insights = fetch_data(get_sqlTemplate(insight_query_key))
    category_data = transform_data(insights)
    save_to_json(category_data, out_dir)
    print(f'saved to json')
    logMsg("Script execution completed.")
    
if __name__ == "__main__":
    main()

"""
Feed Generation Script for Main and Category-Specific Feeds

This script generates and saves JSON feeds for both main and category-specific insights.
It gathers insights from JSON files, filters and trims the data based on configuration (for main feed),
and saves the final feed to specified directories, creating archives as needed.

Dependencies:
- ujson: For fast JSON serialization and deserialization.
- zipfile: For creating archives of the feed files.
- os, json, datetime, random: Standard Python libraries for file handling and processing.

Configuration:
- util_data: Path to utility data directory (set as environment variable or replace with actual path).
- nodejs_data: Path to Node.js data directory (set as environment variable or replace with actual path).

Functions:
- log_msg(message): Logs a message to the console.
- gather_all_json_files(directory, exclude_folder): Gathers all JSON files, excluding specified folders.
- read_json_file(file_path): Reads JSON files and handles JSON decode errors.
- save_batch_file(insights, target_folder, target_file_name): Saves the batch files, handles archiving, and ensures minification using ujson.
- save_category_batch_file(category, insights): Saves individual category batch files at the specified level.
- trim_insights(data): Trims insights data to include essential fields and default images.
- gather_insights_from_directory(directory): Gathers random insights from all category directories.
- filter_insights(insights, config): Filters insights based on configuration criteria.
- main(feed_type): Main function to orchestrate the feed generation process.

Usage:
Run this script with an optional argument to specify the feed type:
- 'main' for generating the main feed.
- 'category' (default) for generating category-specific feeds.

Example:
    python script_name.py main

The default behavior (no arguments) generates category-specific feeds.
"""

import os
import json
import ujson
import zipfile
from datetime import datetime
import random

# Set environment variables or replace with actual paths
util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

# List of filenames to exclude
exclude_filenames = ['main_feed', '_batch']

out_pattern = "batch"
out_type = "json"

def log_msg(message):
    print(message)

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def gather_all_json_files(directory, exclude_folder='main_feed'):
    json_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != exclude_folder]
        for file in files:
            if file.endswith('.json') and not any(exclude in file for exclude in exclude_filenames):
                json_files.append(os.path.join(root, file))
    return json_files

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        log_msg(f"Skipping invalid JSON file: {file_path}")
        return None

def save_batch_file(insights, target_folder, target_file_name):
    target_dir = os.path.join(nodejs_data, content_root, target_folder)
    os.makedirs(target_dir, exist_ok=True)
    archive_dir = os.path.join(target_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_output_path = os.path.join(target_dir, f"{target_file_name}_raw_{timestamp}.json")
    final_output_path = os.path.join(target_dir, target_file_name)
    archive_path = os.path.join(archive_dir, f"{target_file_name}_{timestamp}.zip")
    
    log_msg(f'Insights before saving: {type(insights)}')
    log_msg(f'Insights content: {insights[:2]}')  # Print first 2 items for debugging

    try:
        # Write the raw JSON data using ujson
        with open(raw_output_path, 'w') as f:
            ujson.dump(insights, f, indent=4)
        
        log_msg(f"Batch file raw data saved successfully at {raw_output_path}")

        # Read the raw JSON data using ujson
        with open(raw_output_path, 'r') as f:
            raw_json_data = ujson.load(f)

        # Minify the JSON data by writing it without extra spaces or line breaks
        minimized_json = ujson.dumps(raw_json_data)

        # Archive the previous final output file if it exists
        if os.path.exists(final_output_path):
            timestamped_output_path = f"{final_output_path}_{timestamp}"
            os.rename(final_output_path, timestamped_output_path)
            log_msg(f"Renamed existing batch file to {timestamped_output_path}")

            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.write(raw_output_path, os.path.basename(raw_output_path))
                archive.write(timestamped_output_path, os.path.basename(timestamped_output_path))
                log_msg(f"Archive created successfully at {archive_path}")

            os.remove(timestamped_output_path)
            log_msg(f"Deleted previous batch file after archiving")
        else:
            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.write(raw_output_path, os.path.basename(raw_output_path))
                log_msg(f"Archive created successfully at {archive_path}")

        # Write the minified JSON data
        with open(final_output_path, 'w') as f:
            f.write(minimized_json)

        log_msg(f"Batch file saved successfully at {final_output_path}")

        os.remove(raw_output_path)
        log_msg(f"Deleted raw batch file after archiving")

    except Exception as e:
        log_msg(f"Error during saving: {e}")

def save_category_batch_file(category, insights):
    save_batch_file(insights, category, f"{category}_{out_pattern}.{out_type}")

def trim_insights(data):
    trimmed_insights = []
    for record in data:
        try:
            # Debugging print statements to understand the structure
            #print("Full Record:")
            #print(json.dumps(record, indent=4))  # Use json.dumps for pretty printing
            
            category = record.get('insight_details', {}).get('data_category', 'uncategorized')
            
            # Retrieve default_img from the media section
            media = record.get('media', {})
            default_img = media.get('default_img', 'default image Missing')
            print(f"Default Image Found: {default_img}")
            
            text_block_content = record.get('text_block', {}).get('content', 'No data')[:250]
            text_block_description = record.get('text_block', {}).get('description', 'No description')

            trimmed_record = {
                "insight_details": {
                    "url_id": record.get('insight_details', {}).get('url_id', 'Missing'),
                    "cluster_id": record.get('insight_details', {}).get('cluster_id', 'Missing'),
                    "subject_id": record.get('insight_details', {}).get('subject_id', 'Missing'),
                    "subject_title": record.get('insight_details', {}).get('subject_title', 'Missing'),
                    "data_category": record.get('insight_details', {}).get('data_category', 'Missing'),
                    "data_category_id": record.get('insight_details', {}).get('data_category_id', 'Missing'),
                    "data_subject": record.get('insight_details', {}).get('data_subject', 'Missing'),
                    "data_subject_id": record.get('insight_details', {}).get('data_subject_id', 'Missing'),
                    "content_name": record.get('insight_details', {}).get('content_name', 'Missing')
                },
                "default_img": default_img,
                "text_block": {
                    "content": text_block_content,
                    "description": text_block_description
                }
            }

            trimmed_insights.append(trimmed_record)
        except Exception as e:
            print(f"Error processing record: {e}")
            continue
    return trimmed_insights



def filter_insights(insights, config):
    filtered_insights = []

    for category, details in config['categories'].items():
        category_insights = [insight for insight in insights if insight['insight_details'].get('data_category') == category]
        
        if 'cluster_id' in details:
            category_insights = [insight for insight in category_insights if insight['insight_details'].get('cluster_id') == details['cluster_id']]
        
        max_records = int(details.get('records_to_get', len(category_insights)))
        filtered_insights.extend(category_insights[:max_records])

    return filtered_insights

def gather_all_insights(directory, exclude_folder='main_feed'):
    insights = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != exclude_folder]
        for file in files:
            if file.endswith('.json') and not any(exclude in file for exclude in exclude_filenames):
                file_path = os.path.join(root, file)
                data = read_json_file(file_path)
                if data is None:
                    continue
                if isinstance(data, list):
                    insights.extend(data)
                else:
                    insights.append(data)
    return insights

def main(feed_type='category'):
    log_msg("Gathering all insights from directory...")
    all_insights = gather_all_insights(os.path.join(nodejs_data, content_root))

    if feed_type == 'main':
        config_path = os.path.join(util_data, 'config', 'bkds_contentGen_main_feed_config.json')
        log_msg("Loading configuration...")
        config = load_config(config_path)

        log_msg("Filtering insights based on configuration...")
        filtered_insights = filter_insights(all_insights, config)

        log_msg("Trimming insights...")
        trimmed_insights = trim_insights(filtered_insights)

        log_msg("Saving main feed...")
        save_batch_file(trimmed_insights, config['target_folder'], config['target_file_name'])
        log_msg("Main feed generation completed.")
    else:
        category_insights = {}

        log_msg("Categorizing insights...")
        for record in all_insights:
            category = record.get('insight_details', {}).get('data_category', 'uncategorized')
            if category not in category_insights:
                category_insights[category] = []
            category_insights[category].append(record)

        log_msg("Trimming insights for each category...")
        for category, insights in category_insights.items():
            category_insights[category] = trim_insights(insights)

        log_msg("Saving category-specific batch files...")
        for category, insights in category_insights.items():
            save_category_batch_file(category, insights)
        log_msg("Category feed generation completed.")

if __name__ == "__main__":
    import sys
    feed_type = 'main' if len(sys.argv) > 1 and sys.argv[1] == 'main' else 'category'
    main(feed_type)

"""
Content Feed Generator Script

This script generates a main feed of content from a database of organized JSON files.
The program uses a configuration file to limit the output to specific categories and quantities.

Modules Used:
- os: For directory and file path manipulation
- json, ujson: For JSON file handling
- time, datetime: For time and date operations
- zipfile: For creating zip archives
- random: For random selection of records
- json_minify: For minifying JSON data
- bkdsUtilities: Custom utilities for logging and data fetching

Functionality:
- Load configuration from a JSON file
- Gather insights from JSON files in specified directories
- Filter insights based on configuration settings
- Save the filtered insights to a main feed file, with raw data and minified JSON data
- Archive old batch files to avoid redundancy

Usage:
- Set environment variables BKDS_UTIL_DATA and BKDS_NODEJS_DATA to appropriate paths
- Ensure required modules are installed: json_minify, ujson
- Run the script to generate the content feqed

Author: [Your Name]
Date: [Date]

"""

import os
import json
import ujson
import zipfile
from datetime import datetime
import random
from bkds_Utilities import logMsg

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def logMsg(msg):
    """Log a message to the console and using a logging system."""
    print(msg)

config_path = os.path.join(util_data, 'config', 'bkds_contentGen_main_feed_config.json')
suppression_strings = {"launch_update"}  # Add more suppression strings as needed

#####################################################################
# Main logic and functions

def gather_insights_from_directory(directory):
    logMsg(f'Working with directory: {directory}')
    insights = []
    for category_dir in os.listdir(directory):
        category_path = os.path.join(directory, category_dir)
        if os.path.isdir(category_path):
            for root, _, files in os.walk(category_path):
                json_files = [file for file in files if file.endswith('.json')]
                for json_file in json_files:
                    # Check if the file should be skipped based on suppression strings
                    if any(s.lower() in json_file.lower() for s in suppression_strings):
                        logMsg(f"Skipping suppressed file: {json_file}")
                        continue
                    
                    file_path = os.path.join(root, json_file)
                    with open(file_path, 'r') as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            logMsg(f"Skipping invalid JSON file: {file_path}")
                            continue
                        
                        # Add data if it's a non-empty list
                        if isinstance(data, list) and data:
                            insights.extend(data)
                        else:
                            logMsg(f"No valid records found in {file_path}. Skipping file.")
    return insights


def filter_insights(config, insights):
    logMsg(f'filter_insights: {config}')
    if not isinstance(config, dict):
        raise TypeError("config must be a dictionary")
    
    if 'categories' not in config or not isinstance(config['categories'], dict):
        raise TypeError("config['categories'] must be a dictionary")
    
    filtered_insights = []

    for category, details in config['categories'].items():
        if not isinstance(details, dict):
            continue  # Skip if details is not a dictionary

        category_insights = [
            insight for insight in insights 
            if insight.get('insight_details', {}).get('data_category') == category
        ]

        if 'cluster_id' in details:
            category_insights = [
                insight for insight in category_insights 
                if insight.get('insight_details', {}).get('cluster_id') == details['cluster_id']
            ]

        max_records = int(details.get('records_to_get', len(category_insights)))
        random.shuffle(category_insights)
        filtered_insights.extend(category_insights[:max_records])

    random.shuffle(filtered_insights)
    return filtered_insights


def save_main_feed(filtered_insights, target_folder, target_file_name):
    logMsg(f'save_main_feed: {target_folder}, {target_file_name}')
    target_dir = os.path.join(nodejs_data, content_root, target_folder)
    os.makedirs(target_dir, exist_ok=True)
    archive_dir = os.path.join(target_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    # Add positional index to each insight
    for index, insight in enumerate(filtered_insights):
        insight['data_src_index'] = index

    filtered_insights_sorted = sorted(
        filtered_insights, 
        key=lambda x: x['data_src_index']
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_output_path = os.path.join(target_dir, f"{target_file_name}_raw_{timestamp}.json")
    final_output_path = os.path.join(target_dir, target_file_name)
    archive_path = os.path.join(archive_dir, f"{target_file_name}_{timestamp}.zip")

    try:
        # Write raw JSON data
        with open(raw_output_path, 'w') as f:
            ujson.dump(filtered_insights_sorted, f)
        logMsg(f"Main feed raw batch file saved successfully at {raw_output_path}")

        # Check for existing data
        existing_data = None
        if os.path.exists(final_output_path):
            if os.path.getsize(final_output_path) > 0:  # File is not empty
                try:
                    with open(final_output_path, 'r') as f:
                        existing_data = ujson.load(f)
                except ujson.JSONDecodeError as e:
                    with open(final_output_path, 'r') as f:
                        raw_content = f.read()
                    logMsg(f"Malformed JSON in existing file: {final_output_path}. Error: {e}. Content: {raw_content}")
                    existing_data = None
            else:
                logMsg(f"Existing file is empty: {final_output_path}")
        
        # Serialize data for comparison
        existing_data_serialized = ujson.dumps(existing_data) if existing_data else None
        new_data_serialized = ujson.dumps(filtered_insights_sorted)

        if existing_data_serialized == new_data_serialized:
            logMsg("No changes detected. Skipping write.")
            os.remove(raw_output_path)
            return

        # Write new data
        with open(final_output_path, 'w') as f:
            f.write(new_data_serialized)
        logMsg(f"Main feed batch file saved successfully at {final_output_path}")

        # Archive old files
        with zipfile.ZipFile(archive_path, 'w') as archive:
            archive.write(raw_output_path, os.path.basename(raw_output_path))
        logMsg(f"Archive created successfully at {archive_path}")

        os.remove(raw_output_path)
        logMsg("Raw batch file deleted after archiving.")

    except Exception as e:
        logMsg(f"Error during saving: {e}")
        raise


def normalize_for_json(data):
    """Recursively normalize data for JSON serialization."""
    if isinstance(data, (list, tuple)):
        return [normalize_for_json(item) for item in data]
    elif isinstance(data, dict):
        return {key: normalize_for_json(value) for key, value in data.items()}
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    else:
        return str(data)  # Convert unsupported types to string

def main():
    logMsg("Loading configuration...")
    config = load_config(config_path)
    
    logMsg("Gathering insights from directory...")
    insights = gather_insights_from_directory(os.path.join(nodejs_data, content_root))
    
    logMsg("Filtering insights based on configuration...")
    filtered_insights = filter_insights(config, insights)  # Correct order of parameters

    trimmed_insights = []
    skipped_count = 0  # Counter for skipped records

    for insight in filtered_insights:
        #logMsg(f"Processing insight: {insight.get('insight_details', {}).get('url_id', 'Unknown ID')}")
        if 'media' in insight:
            default_image = insight['media'].get('default_img')
        
            # Add default image URL to trimmed_insights
            trimmed_record = {
                "insight_details": {
                    "url_id": insight['insight_details'].get('url_id', 'Missing'),
                    "cluster_id": insight['insight_details'].get('cluster_id', 'Missing'),
                    "subject_id": insight['insight_details'].get('subject_id', 'Missing'),
                    "subject_title": insight['insight_details'].get('subject_title', 'Missing'),
                    "data_category": insight['insight_details'].get('data_category', 'Missing'),
                    "data_category_id": insight['insight_details'].get('data_category_id', 'Missing'),
                    "data_subject": insight['insight_details'].get('data_subject', 'Missing'),
                    "data_subject_id": insight['insight_details'].get('data_subject_id', 'Missing'),
                    "content_name": insight['insight_details'].get('content_name', 'Missing')
                },
                "default_img": default_image,
                "text_block": {
                    "content": insight.get('text_block', {}).get('content', 'No data')[:250],
                    "description": insight.get('text_block', {}).get('description', 'No description data')
                }
            }

            trimmed_insights.append(trimmed_record)
        else:
            skipped_count += 1  # Increment skipped counter
            #logMsg(f"Skipped {insight}")

    logMsg(f"Processed {len(trimmed_insights)} insights")
    logMsg(f"Skipped {skipped_count} non-media records")  # Log the number of skipped records
    
    logMsg("Saving main feed...")
    save_main_feed(trimmed_insights, config['target_folder'], config['target_file_name'])
    
    logMsg("Main feed generation completed.")

if __name__ == "__main__":
    main()
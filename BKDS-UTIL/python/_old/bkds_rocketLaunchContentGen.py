import os
import glob
import json
import random
from datetime import datetime
import socket
import argparse
import zipfile
from bkdsUtilities import log_msg
from pathlib import Path

"""
Rocket Launch Data Aggregator

This script aggregates rocket launch data from multiple JSON files in a specified directory,
extracts relevant details, and generates a consolidated output JSON file with the latest rocket launch,
related videos, images, and topics.

Usage:
    python script_name.py <batch_id>

Arguments:
    batch_id  Batch ID for the current run

Environment Variables:
    BKDS_AUTO         Base directory for utilities data
    BKDS_NODEJS_DATA  Base directory for Node.js data
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description="Aggregate rocket launch data and generate a consolidated output JSON file.")
    parser.add_argument("batch_id", help="Batch ID for the current run")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
program_name = os.path.basename(__file__)

util_data = os.getenv('BKDS_AUTO')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

hostname = socket.gethostname()
hostname='bkds-pc-00x'
current_date = datetime.now().strftime('%Y%m%d')
api_folder = 'BKDS_REPORTING_DATA_ROCKET_LAUNCH'
rocket_api_data_folder = os.path.join(util_data, 'reporting', 'data', hostname, current_date, api_folder)

content_root = 'content_feeds'
content_dir = os.path.join(nodejs_data, content_root)
rocket_content_dir=os.path.join(content_dir, 'rockets')
main_feed_content_dir=os.path.join(content_dir, 'main_feed')

rocket_file_json_data = 'rockets_batch.json'
rocket_file_related_topic_json_data = os.path.join(rocket_content_dir, rocket_file_json_data)
rocket_file_pattern = '*_ROCKET_LAUNCH_*_insight_*'

launch_cluster = 'launches'
launch_subject_id = 'launch_update_1ad015753ff5ae2e93060a76080d4031'
launch_category = 'rockets'
launch_data_subject = 'rocket_launches'
launch_url_id = 'launch_update_1ad015753ff5ae2e93060a76080d4031'
launch_content_name = 'rocket_launches'
launch_category_id = 'launch_update_1ad015753ff5ae2e93060a76080d4031'
launch_desc_key = 'launch_desc'
title_key = "launch_mission"

output_dir = os.path.join(rocket_content_dir, launch_cluster, launch_url_id)
out_type = "json"
output_file = f'{launch_url_id}_{launch_category}.{out_type}'
output_filepath = os.path.join(output_dir, output_file)
main_feed_filename='main_feed_batch.json'
main_feed_content_filepath=os.path.join(main_feed_content_dir, main_feed_filename)


def logMsg(msg):
    """Log a message to the console and using a logging system."""
    log_msg(program_name, batch_id, msg)
    print(f"[{program_name}][{batch_id}] {msg}")

def read_latest_json_file(directory, pattern):
    logMsg(f'read_latest_json_file directory {directory}')
    logMsg(f'read_latest_json_file pattern {pattern}')

    file_pattern = os.path.join(directory, pattern)
    files = glob.glob(file_pattern)
    latest_file = max(files, key=os.path.getmtime) if files else None

    if latest_file:
        with open(latest_file, 'r') as f:
            try:
                content = json.load(f)
                logMsg(f"Successfully read file: {latest_file}")
                return content
            except json.JSONDecodeError as e:
                logMsg(f"Error decoding JSON from file {latest_file}: {e}")
    return None

def get_related_topics_and_images(filepath):
    logMsg(f'get_related_topics_and_images {filepath}')

    with open(filepath, 'r') as f:
        data = json.load(f)
    
    related_topics = []
    images = []

    for item in data:
        insight_details = item.get("insight_details", {})
        default_img = item.get("default_img", "")
        
        related_topics.append({
            "url_id": insight_details.get("url_id", ""),
            "cluster_id": insight_details.get("cluster_id", ""),
            "data_category": insight_details.get("data_category", ""),
            "subject_title": insight_details.get("subject_title", ""),
            "data_category_id": insight_details.get("data_category_id", "")
        })

        images.append({
            "img_url_id": insight_details.get("url_id", ""),
            "img_url": default_img,
            "img_title": insight_details.get("subject_title", ""),
            "img_desc1": insight_details.get("subject_title", ""),
            "img_desc2": "",
            "img_src": "consolidated_batch_file",
            "data_category": insight_details.get("data_category", ""),
            "data_subject": insight_details.get("data_subject", ""),
            "label": "featured"
        })

    random.shuffle(related_topics)
    random.shuffle(images)

    logMsg("Extracted and shuffled related topics and images.")
    return related_topics, images

def generate_content_block(latest_launch):
    if not latest_launch:
        return "NO DATA"
    
    mission = latest_launch.get('launch_mission', 'N/A')
    pad_name = latest_launch.get('launch_pad_name', 'N/A')
    pad_country = latest_launch.get('launch_pad_country', 'N/A')
    purpose = latest_launch.get('launch_purpose', 'N/A')
    est_time = latest_launch.get('launch_est_time', 'N/A')
    description = latest_launch.get('launch_desc', 'N/A').replace('\n', '<br>')
    quicktext = latest_launch.get('launch_quicktext', 'N/A')
    last_update = latest_launch.get('launch_last_update', 'N/A')
    watch_link = latest_launch.get('launch_quicktext', '').split(' - ')[-1]

    content = (
        f"<strong>Mission:</strong> {mission}<br>"
        f"<strong>Launch Pad:</strong> {pad_name} ({pad_country})<br>"
        f"<strong>Purpose:</strong> {purpose}<br>"
        f"<strong>Estimated Launch Time:</strong> {est_time}<br>"
        f"<strong>Description:</strong> {description}<br>"
        f"<strong>Quick Text:</strong> {quicktext}<br>"
        f"<strong>Last Update:</strong> {last_update}<br>"
        f"<strong>Watch Live:</strong> <a href='{watch_link}'>Link</a>"
    )

    return content

def generate_output_json(latest_launch, videos, images, related_topics):
    content = generate_content_block(latest_launch)
    output = [
        {
            "insight_details": {
                "url_id": launch_url_id,
                "cluster_id": launch_cluster,
                "subject_id": launch_subject_id,
                "subject_title": latest_launch.get(title_key, "") if latest_launch else "",
                "data_category": launch_category,
                "data_category_id": launch_category_id,
                "data_subject": launch_data_subject,
                "data_subject_id": launch_subject_id,
                "content_name": launch_content_name
            },
            "text_block": {
                "source": "",
                "content": content,
                "description": "Overview of " + (latest_launch.get(title_key, "") if latest_launch else "NO DATA")
            },
            "media": {
                "videos": videos,
                "images": images,
                "related_topics": related_topics
            }
        }
    ]
    logMsg("Generated output JSON structure.")
    return output

import os
import json
import random
import zipfile
from datetime import datetime
from pathlib import Path

def logMsg(message):
    print(message)

def save_output_json(output, filepath, main_feed_content_filepath):
    # Ensure the output directory exists
    output_dir = os.path.dirname(filepath)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if the file already exists
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            existing_data = json.load(f)
        
        # Compare the existing file with the new output
        if existing_data == output:
            logMsg("No changes detected. Output JSON not saved.")
            return
        else:
            # Archive the existing file
            archive_dir = os.path.join(output_dir, 'archive')
            os.makedirs(archive_dir, exist_ok=True)
            
            # Create a zip file for the archived JSON file
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = os.path.join(archive_dir, f"{Path(filepath).stem}_{current_date}.zip")
            with zipfile.ZipFile(archive_file, 'w') as zipf:
                zipf.write(filepath, os.path.basename(filepath))
            
            logMsg(f"Archived existing JSON file to {archive_file}")
    
    # Write the new output JSON file
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    logMsg(f"Output JSON saved to {filepath}")

    # Update the main_feed_content_file with the insight_details section
    new_insight_details = output[0]["insight_details"]
    main_feed_content = []

    # Check if the main_feed_content_file exists
    if os.path.exists(main_feed_content_filepath):
        with open(main_feed_content_filepath, 'r') as f:
            main_feed_content = json.load(f)

    # Remove existing entry with the same url_id if it exists
    main_feed_content = [entry for entry in main_feed_content if entry.get('insight_details', {}).get('url_id') != new_insight_details.get('url_id')]

    # Shuffle the top 5 entries
    top_six_entries = main_feed_content[:5]  # Get the first 5 entries
    random.shuffle(top_six_entries)  # Shuffle these entries

    # Insert the new entry at a random position within the top 6
    insert_position = random.randint(0, 5)
    top_six_entries.insert(insert_position, {"insight_details": new_insight_details})

    # Combine the shuffled top 6 entries with the rest of the feed
    main_feed_content = top_six_entries + main_feed_content[5:]

    # Write the updated main_feed_content to the main_feed_content_filepath
    with open(main_feed_content_filepath, 'w') as f:
        json.dump(main_feed_content, f, indent=2)

    logMsg(f"Updated main_feed_content_file with new insight_details.")

    
def main():
    logMsg("Starting the aggregation process.")
    
    latest_launch = read_latest_json_file(rocket_api_data_folder, rocket_file_pattern)
    if latest_launch:
        logMsg(f"Latest launch data: {latest_launch}")
    else:
        logMsg("No latest launch data found.")
    
    videos = []  # Placeholder for future video extraction logic
    related_topics, images = get_related_topics_and_images(rocket_file_related_topic_json_data)
    
    output = generate_output_json(latest_launch, videos, images, related_topics)
    save_output_json(output, output_filepath, main_feed_content_filepath)
    logMsg("Aggregation process completed successfully.")

if __name__ == "__main__":
    main()
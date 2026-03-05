import os
import glob
import json
import random
from datetime import datetime
import socket
import argparse
import zipfile
from pathlib import Path
from bkds_Utilities import log_msg

##################################
# Rocket Launch Data Aggregator
# Setup and global variables

##################################
# Rocket Launch Data Aggregator - Setup and Global Variables
def parse_arguments():
    parser = argparse.ArgumentParser(description="Aggregate rocket launch data and generate a consolidated output JSON file.")
    parser.add_argument("batch_id", help="Batch ID for the current run")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
# Environment variables
util_data = os.getenv('BKDS_AUTO')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

# Program identifiers
program_name = os.path.basename(__file__)
hostname = socket.gethostname()
current_date = datetime.now().strftime('%Y%m%d')

# Directory and File Paths
API_FOLDER = batch_id
CONTENT_ROOT = 'content_feeds'
rocket_api_data_folder = os.path.join(util_data, 'reporting', 'data', hostname, current_date, API_FOLDER)
content_dir = os.path.join(nodejs_data, CONTENT_ROOT)
rocket_content_dir = os.path.join(content_dir, 'rockets')
main_feed_content_dir = rocket_content_dir

# File Names and Patterns
OUTPUT_TYPE = "json"
ROCKET_FILE_JSON = 'rockets_batch.json'
ROCKET_FILE_PATTERN = f'*{batch_id}*_insight_*'
VIDEO_INDEX_FILE = 'bkds_yt_launches.json'
rocket_file_related_topic_json = os.path.join(rocket_content_dir, ROCKET_FILE_JSON)
video_index_filepath = os.path.join(content_dir, 'rockets', 'launches', VIDEO_INDEX_FILE)

# Output Paths
output_dir = os.path.join(rocket_content_dir, 'launches', 'launch_update_1ad015753ff5ae2e93060a76080d4031')
output_file = f'launch_update_1ad015753ff5ae2e93060a76080d4031_rockets.{OUTPUT_TYPE}'
output_filepath = os.path.join(output_dir, output_file)
main_feed_filename = 'rockets_batch.json'
main_feed_content_filepath = os.path.join(main_feed_content_dir, main_feed_filename)

# Launch Data Constants
LAUNCH_CLUSTER = 'launches'
LAUNCH_SUBJECT_ID = 'launch_update_c339792c1afdd1e815def3398efd80c7'
LAUNCH_CATEGORY = 'rockets'
LAUNCH_DATA_SUBJECT = 'rocket_launches'
LAUNCH_URL_ID = 'launch_update_1ad015753ff5ae2e93060a76080d4031'
LAUNCH_CONTENT_NAME = 'rocket_launches'
LAUNCH_CATEGORY_ID = 'launch_update_c6e83965fedb97e17664cf3bc6171235'
DEFAULT_IMG = '/img/bkds_UI_rockets.png'

# JSON Key Constants
URL_ID_KEY = "url_id"
CLUSTER_ID_KEY = "cluster_id"
SUBJECT_ID_KEY = "subject_id"
SUBJECT_TITLE_KEY = "subject_title"
DATA_CATEGORY_KEY = "data_category"
DATA_CATEGORY_ID_KEY = "data_category_id"
DATA_SUBJECT_KEY = "data_subject"
DATA_SUBJECT_ID_KEY = "data_subject_id"
CONTENT_NAME_KEY = "content_name"
INSIGHT_DETAILS_KEY = "insight_details"
TEXT_BLOCK_KEY = "text_block"
CONTENT_KEY = "content"
DESCRIPTION_KEY = "description"
MEDIA_KEY = "media"
VIDEOS_KEY = "videos"
IMAGES_KEY = "images"
RELATED_TOPICS_KEY = "related_topics"
DEFAULT_IMG_KEY = "default_img"
TITLE_KEY = "title"
URL_KEY = "url"

# Additional Media-Related JSON Keys
IMG_URL_ID_KEY = "img_url_id"
IMG_URL_KEY = "img_url"
IMG_TITLE_KEY = "img_title"
IMG_DESC1_KEY = "img_desc1"
IMG_DESC2_KEY = "img_desc2"
IMG_SRC_KEY = "img_src"
VID_TITLE_KEY = "vid_title"
VID_DESCRIPTION_KEY = "vid_description"
VID_THUMB_URL_KEY = "vid_thumb_url"
VID_URL_KEY = "vid_url"
VID_TIMESTAMP_KEY = "vid_timestamp"
LABEL_KEY = "label"

# Launch Information Keys
MISSION_KEY = 'launch_mission'
PAD_NAME_KEY = 'launch_pad_name'
PAD_COUNTRY_KEY = 'launch_pad_country'
PURPOSE_KEY = 'launch_purpose'
EST_TIME_KEY = 'launch_est_time'
DESCRIPTION_KEY = 'launch_desc'
QUICKTEXT_KEY = 'launch_quicktext'
LAST_UPDATE_KEY = 'launch_last_update'
DEFAULT_VALUE = 'N/A'

# HTML Formatting Labels
MISSION_LABEL = "Mission"
LAUNCH_PAD_LABEL = "Launch Pad"
PURPOSE_LABEL = "Purpose"
ESTIMATED_TIME_LABEL = "Estimated Launch Time"
DESCRIPTION_LABEL = "Description"
WATCH_LINK_LABEL = "Check for video update"
LAST_UPDATE_LABEL = "Last Update"

# Image and Video Properties
CONSOLIDATED_BATCH_FILE = "consolidated_batch_file"
FEATURED_LABEL = "featured"
THUMB_KEY = "thumbnail"
TIME_STAMP_KEY = "timestamp"
ARCHIVE_SUBDIR = 'archive'
DEFAULT_IMAGE_PATH = "/img/bkds_UI_rockets.png"

# Formatting and Limits
TIME_FORMAT = "%Y%m%d_%H%M%S"
MAX_RELATED_TOPICS = 150
LAUNCH_UPDATE = "ROCKET LAUNCH UPDATE"
TIME_STAMP="timestamp"
THUMB="thumbnail"

# Utility functions
def logMsg(msg):
    """Log a message to the console and using a logging system."""
    log_msg(program_name, batch_id, msg)
    print(f"[{program_name}][{batch_id}] {msg}")

##################################
# Main logic and functions

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

def generate_content_block(latest_launch):
    if not latest_launch:
        return "NO DATA"
    
    # Extract values with defaults
    mission = latest_launch.get(MISSION_KEY, DEFAULT_VALUE)
    pad_name = latest_launch.get(PAD_NAME_KEY, DEFAULT_VALUE)
    pad_country = latest_launch.get(PAD_COUNTRY_KEY, DEFAULT_VALUE)
    purpose = latest_launch.get(PURPOSE_KEY, DEFAULT_VALUE)
    est_time = latest_launch.get(EST_TIME_KEY, DEFAULT_VALUE)
    description = latest_launch.get(DESCRIPTION_KEY, DEFAULT_VALUE)
    #quicktext = latest_launch.get(QUICKTEXT_KEY, DEFAULT_VALUE)
    last_update = latest_launch.get(LAST_UPDATE_KEY, DEFAULT_VALUE)
    watch_link = extract_url(latest_launch.get(QUICKTEXT_KEY, '').split(' - ')[-1])

    # Format description with line breaks
    description_formatted = description.replace('\n', '<br>')

    # Construct the content block
    content = (
        f"<p><strong>{MISSION_LABEL}:</strong> {mission}</p>"
        f"<p><strong>{LAUNCH_PAD_LABEL}:</strong> {pad_name} ({pad_country})</p>"
        f"<p><strong>{PURPOSE_LABEL}:</strong> {purpose}</p>"
        f"<p><strong>{ESTIMATED_TIME_LABEL}:</strong> {est_time}</p>"
        f"<p><strong>{DESCRIPTION_LABEL}:</strong> {description_formatted}</p>"
        f"<p><strong><a class='button-link' href='{watch_link}'>{WATCH_LINK_LABEL}</a></strong></p>"
        f"<p><strong>{LAST_UPDATE_LABEL}:</strong> {last_update}</p>"
    )

    return content

def extract_url(text):
    """Extract the URL from the given text by breaking at the first space."""
    return text.split(' ')[0] if text else ''

def generate_output_json(latest_launch, videos, images, related_topics):
    content = generate_content_block(latest_launch)
    output = [
        {
            INSIGHT_DETAILS_KEY: {
                URL_ID_KEY: LAUNCH_URL_ID,
                CLUSTER_ID_KEY: LAUNCH_CLUSTER,
                SUBJECT_ID_KEY: LAUNCH_SUBJECT_ID,
                SUBJECT_TITLE_KEY: latest_launch.get(SUBJECT_TITLE_KEY, "") if latest_launch else "Rocket Launch Update",
                DATA_CATEGORY_KEY: LAUNCH_CATEGORY,
                DATA_CATEGORY_ID_KEY: LAUNCH_CATEGORY_ID,
                DATA_SUBJECT_KEY: LAUNCH_DATA_SUBJECT,
                DATA_SUBJECT_ID_KEY: LAUNCH_SUBJECT_ID,
                CONTENT_NAME_KEY: LAUNCH_CONTENT_NAME
            },
            DEFAULT_IMG_KEY: DEFAULT_IMG,
            TEXT_BLOCK_KEY: {
                CONTENT_KEY: content,
                DESCRIPTION_KEY: "Overview of " + (latest_launch.get(SUBJECT_TITLE_KEY, "") if latest_launch else f"NO DATA FROM ${SUBJECT_TITLE_KEY}")
            },
            MEDIA_KEY: {
                VIDEOS_KEY: videos,
                IMAGES_KEY: images,
            },
            RELATED_TOPICS_KEY: related_topics
        }
    ]
    logMsg("Generated output JSON structure.")
    return output

def get_video_details(filepath):
    logMsg(f'get_video_details {filepath}')

    with open(filepath, 'r') as f:
        data = json.load(f)
    
    videos = []
    for item in data:
        videos.append({
            VID_TITLE_KEY: item.get(TITLE_KEY, ""),
            VID_DESCRIPTION_KEY: item.get(DESCRIPTION_LABEL, ""),
            VID_THUMB_URL_KEY: item.get(THUMB, ""),
            VID_URL_KEY: item.get(URL_KEY, ""),
            VID_TIMESTAMP_KEY: item.get(TIME_STAMP, "")
        })
    
    logMsg("Extracted video details.")
    return videos

def save_output_json(output, filepath, main_feed_content_filepath):
    """Save JSON data to output file, archive if existing, and update main feed content file."""

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
            archive_dir = os.path.join(output_dir, ARCHIVE_SUBDIR)
            os.makedirs(archive_dir, exist_ok=True)
            
            # Create a zip file for the archived JSON file
            current_date = datetime.now().strftime(TIME_FORMAT)
            archive_file = os.path.join(archive_dir, f"{Path(filepath).stem}_{current_date}.zip")
            with zipfile.ZipFile(archive_file, 'w') as zipf:
                zipf.write(filepath, os.path.basename(filepath))
            
            logMsg(f"Archived existing JSON file to {archive_file}")
    
    # Write the new output JSON file
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    logMsg(f"Output JSON saved to {filepath}")

    # Update the main_feed_content_file with a trimmed down version of the insight details
    new_insight_details = output[0][INSIGHT_DETAILS_KEY]
    main_feed_content = []

    # Check if the main_feed_content_file exists
    if os.path.exists(main_feed_content_filepath):
        with open(main_feed_content_filepath, 'r') as f:
            main_feed_content = json.load(f)

    # Search for existing entry in the main feed content
    existing_entry = next(
        (entry for entry in main_feed_content if entry.get(INSIGHT_DETAILS_KEY, {}).get(URL_ID_KEY) == new_insight_details.get(URL_ID_KEY)), 
        None
    )

    limited_output = {
        INSIGHT_DETAILS_KEY: {
            URL_ID_KEY: new_insight_details[URL_ID_KEY],
            CLUSTER_ID_KEY: new_insight_details[CLUSTER_ID_KEY],
            SUBJECT_ID_KEY: new_insight_details[SUBJECT_ID_KEY],
            SUBJECT_TITLE_KEY: new_insight_details[SUBJECT_TITLE_KEY],
            DATA_CATEGORY_KEY: new_insight_details[DATA_CATEGORY_KEY],
            DATA_CATEGORY_ID_KEY: new_insight_details[DATA_CATEGORY_ID_KEY],
            DATA_SUBJECT_KEY: new_insight_details[DATA_SUBJECT_KEY],
            DATA_SUBJECT_ID_KEY: new_insight_details[DATA_SUBJECT_ID_KEY],
            CONTENT_NAME_KEY: new_insight_details[CONTENT_NAME_KEY]
        },
        DEFAULT_IMG_KEY: DEFAULT_IMAGE_PATH,
        TEXT_BLOCK_KEY: {
            CONTENT_KEY: output[0][TEXT_BLOCK_KEY][CONTENT_KEY],
            DESCRIPTION_KEY: output[0][TEXT_BLOCK_KEY][DESCRIPTION_KEY]
        }
    }

    # Update main feed content with new or changed entry
    if existing_entry:
        if existing_entry != limited_output:
            main_feed_content = [
                entry for entry in main_feed_content 
                if entry.get(INSIGHT_DETAILS_KEY, {}).get(URL_ID_KEY) != new_insight_details.get(URL_ID_KEY)
            ]
            main_feed_content.insert(0, limited_output)
            logMsg(f"Updated existing entry for mission: {new_insight_details.get(SUBJECT_TITLE_KEY)}")
        else:
            logMsg(f"No changes detected for the existing mission. {main_feed_content_filepath} feed not updated.")
            return
    else:
        main_feed_content.insert(0, limited_output)
        logMsg(f"Added new entry for mission: {new_insight_details.get(SUBJECT_TITLE_KEY)}")
    
    # Save updated main feed content to file
    with open(main_feed_content_filepath, 'w') as f:
        json.dump(main_feed_content, f, indent=2)

    logMsg(f"Updated {main_feed_content_filepath} Feed with new or updated insight_details.")

def get_related_topics_and_images(filepath):
    logMsg(f'get_related_topics_and_images {filepath}')

    with open(filepath, 'r') as f:
        data = json.load(f)
    
    related_topics = []
    images = []

    for item in data:
        insight_details = item.get(INSIGHT_DETAILS_KEY, {})
        default_img = item.get(DEFAULT_IMG_KEY, "")
        
        related_topics.append({
            URL_ID_KEY: insight_details.get(URL_ID_KEY, ""),
            CLUSTER_ID_KEY: insight_details.get(CLUSTER_ID_KEY, ""),
            DATA_CATEGORY_KEY: insight_details.get(DATA_CATEGORY_KEY, ""),
            SUBJECT_TITLE_KEY: insight_details.get(SUBJECT_TITLE_KEY, ""),
            DATA_CATEGORY_ID_KEY: insight_details.get(DATA_CATEGORY_ID_KEY, "")
        })

        images.append({
            IMG_URL_ID_KEY: insight_details.get(URL_ID_KEY, ""),
            IMG_URL_KEY: default_img,
            IMG_TITLE_KEY: insight_details.get(SUBJECT_TITLE_KEY, ""),
            IMG_DESC1_KEY: insight_details.get(SUBJECT_TITLE_KEY, ""),
            IMG_DESC2_KEY: "",
            IMG_SRC_KEY: CONSOLIDATED_BATCH_FILE,
            DATA_CATEGORY_KEY: insight_details.get(DATA_CATEGORY_KEY, ""),
            DATA_SUBJECT_KEY: insight_details.get(DATA_SUBJECT_KEY, ""),
            LABEL_KEY: FEATURED_LABEL
        })

    # Shuffle and limit related topics and images
    random.shuffle(related_topics)
    related_topics = related_topics[:MAX_RELATED_TOPICS]

    random.shuffle(images)

    logMsg("Extracted and shuffled related topics and images.")
    return related_topics, images
  
def main():
    logMsg("Starting the aggregation process.")
    
    latest_launch = read_latest_json_file(rocket_api_data_folder, ROCKET_FILE_PATTERN)
    if latest_launch:
        logMsg(f"Latest launch data: {latest_launch}")
        videos = get_video_details(video_index_filepath)
        related_topics, images = get_related_topics_and_images(rocket_file_related_topic_json)

        output = generate_output_json(latest_launch, videos, images, related_topics)
        save_output_json(output, output_filepath, main_feed_content_filepath)
        logMsg("Rocket Launch Post Generation completed successfully.")
    else:
        logMsg("No latest launch data found.")
        return

if __name__ == "__main__":
    main()
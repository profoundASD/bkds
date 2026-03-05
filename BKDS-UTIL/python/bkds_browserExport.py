#!/usr/bin/env python3

"""
Chrome History Exporter

This script exports Chrome browser history to JSON files. It creates both a full
history file and a condensed version excluding localhost entries. The script
handles database locking by copying the history database before reading it.
It also archives any existing files before overwriting them.

Usage:
    ./chrome_history_exporter.py <batch_id>

Environment Variables:
    BKDS_UTIL_DATA        - Base path for utility data
    BKDS_NODEJS_DATA      - Base path for Node.js data
    BKDS_REPORTING_DATA   - Base path for reporting data
"""

import sqlite3
import json
import os
import time
import shutil
import socket
import hashlib
import re
import argparse
from datetime import datetime
from bkds_Utilities import log_msg
#####################################################################
# Main Setup / Variables

def parse_arguments():
    parser = argparse.ArgumentParser(description="Export Chrome history given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    return parser.parse_args()

args = parse_arguments()
BATCH_ID = args.batch_id
PROGRAM_NAME = os.path.basename(__file__)
# Configuration variables
USER_HOME = os.path.expanduser("~")
HOSTNAME = socket.gethostname()
CURRENT_DATE = datetime.now().strftime("%Y%m%d")
TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")

# Environment variables
UTIL_DATA = os.getenv('BKDS_UTIL_DATA', '/default/path/for/util_data')
NODEJS_DATA = os.getenv('BKDS_NODEJS_DATA', '/default/path/for/nodejs_data')
RPT_DATA_OUT = os.getenv('BKDS_REPORTING_DATA', '/default/path/for/reporting_data')

# Log the environment variables and working directory
print(f"NODEJS_DATA: {NODEJS_DATA}")
print(f"Current Working Directory: {os.getcwd()}")

# Directory and file paths for reporting data
DATA_FOLDER_NAME = 'browser_hist'
BASE_FILE_NAME = DATA_FOLDER_NAME
APP_HIST_FILENAME = f'{BASE_FILE_NAME}_batch.json'
FULL_HIST_FILENAME = f'{BASE_FILE_NAME}_full_batch.json'
ARCHIVE_FOLDER = "archive"

RPT_DATA_OUT_FOLDER = os.path.join(RPT_DATA_OUT, HOSTNAME, CURRENT_DATE, BATCH_ID)
RPT_DATA_CONDENSED_HIST = os.path.join(RPT_DATA_OUT_FOLDER, APP_HIST_FILENAME)
RPT_DATA_FULL_HIST = os.path.join(RPT_DATA_OUT_FOLDER, FULL_HIST_FILENAME)
RPT_ARCHIVE_DIR = os.path.join(RPT_DATA_OUT_FOLDER, ARCHIVE_FOLDER)

# Directory and file paths for application data
APP_DATA_PARENT_FOLDER = 'content_feeds'
APP_DATA_OUT_FOLDER = os.path.join(NODEJS_DATA, APP_DATA_PARENT_FOLDER, DATA_FOLDER_NAME)
APP_DATA_CONDENSED_HIST = os.path.join(APP_DATA_OUT_FOLDER, APP_HIST_FILENAME)
APP_ARCHIVE_DIR = os.path.join(APP_DATA_OUT_FOLDER, ARCHIVE_FOLDER)

CHROME_PROF_DEFAULT=".config/google-chrome/Default/History"
CHROME_PROF_USER1 = os.path.join(".config", "google-chrome", "Profile 1", "History")
CHROME_APP_HIST_PATH = os.path.join(USER_HOME,CHROME_PROF_USER1)
CHROME_DB="chrome_history_copy.db"
CHROMHIST_DB_COPY = os.path.join(RPT_DATA_OUT_FOLDER, CHROME_DB)

# Local paths to default images
GOOGLE_MAPS_DEFAULT_IMG = "/path/to/google_maps_default.jpg"
GOOGLE_EARTH_DEFAULT_IMG = "/path/to/google_earth_default.jpg"
WIKIPEDIA_DEFAULT_IMG = "/path/to/wikipedia_default.jpg"

ICON_DATA_PATH = os.path.join(NODEJS_DATA, "config", "bkds_IconData.json")

print(f"ICON_DATA_PATH: {ICON_DATA_PATH}")

#####################################################################
# Main logic and functions

def logMsg(msg):
    """Log a message to the console and using a logging system."""
    log_msg(PROGRAM_NAME, BATCH_ID, msg)
    print(msg)

def copy_history_db(src_path, dest_path):
    logMsg(f'Copying history database from {src_path} to {dest_path}')
    shutil.copy2(src_path, dest_path)

def fetch_history_from_copy(db_copy_path):
    logMsg(f'Fetching history from copied database {db_copy_path}')
    conn = sqlite3.connect(db_copy_path)
    cursor = conn.cursor()
    
    query = """
    SELECT urls.url, urls.title, urls.visit_count, urls.typed_count, visits.visit_time
    FROM urls, visits
    WHERE urls.id = visits.url
    """
    
    cursor.execute(query)
    history = {}
    
    for row in cursor.fetchall():
        url, title, visit_count, typed_count, visit_time = row
        if url not in history or visit_time > history[url]['visit_time']:
            history[url] = {
                "url": url,
                "title": title,
                "visit_count": visit_count,
                "typed_count": typed_count,
                "visit_time": visit_time
            }
    
    cursor.close()
    conn.close()
    
    # Sort history by visit_time, most recent first
    return sorted(list(history.values()), key=lambda x: x['visit_time'], reverse=True)

def generate_url_id(url):
    return hashlib.md5(url.encode()).hexdigest()

def generate_thumbnail_link(youtube_url):
    #logMsg(f'Generating thumbnail link for {youtube_url}')
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", youtube_url)
    if video_id_match:
        video_id = video_id_match.group(1)
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return None

def get_default_img(url, icon_data, subject_title):
    if "music.youtube" in url:
        return generate_thumbnail_link(url)
    elif "youtube.com" in url:
        return generate_thumbnail_link(url)
    else:
        # Use get_insight_src_icon logic to get the appropriate icon from the JSON file
        #logMsg(f'Getting default image for {url}')
        filter_category = None
        site_count = subject_title.count("site:") if subject_title else 0
        
        if site_count > 3:
            filter_category = "toolbar_search_general"
        elif "flickr.com" in url:
            filter_category = "toolbar_search_flickr"
        elif "maps.google.com" in url:
            filter_category = "toolbar_search_gmaps"
        elif "google.com/maps" in url:
            filter_category = "toolbar_search_gmaps"
        elif "earth.google.com" in url:
            filter_category = "toolbar_search_earth"
        elif "google.com/earth" in url:
            filter_category = "toolbar_search_earth"
        elif "wikipedia.org" in url:
            filter_category = "toolbar_search_wikipedia"
        elif "youtube" in url:
            filter_category = "toolbar_search_youtube"
        elif "wikimedia.org" in url:
            filter_category = "toolbar_search_wikimedia"
    
        else:
            filter_category = "toolbar_search_general"

        for icon in icon_data:
            if icon['filterCategory'] == filter_category:
                return icon.get('src', "")
        return "/data/images/full_size/web_history/default.jpg"


def load_icon_data():
    try:
        logMsg(f'Loading icon data from {ICON_DATA_PATH}')
        with open(ICON_DATA_PATH, 'r') as f:
            icon_data = json.load(f)
            logMsg('Finished loading icon data')
        return [icon for icon in icon_data if icon.get('type') == 'toolbar_search_speech_result']
    except FileNotFoundError as e:
        logMsg(f'Error: Icon data file not found: {ICON_DATA_PATH}')
        return []
    except json.JSONDecodeError as e:
        logMsg(f'Error: Failed to decode JSON from {ICON_DATA_PATH}: {str(e)}')
        return []

def get_insight_src_icon(url, icon_data, subject_title):
    logMsg(f'Getting insight source icon for {url}')
    filter_category = None
    site_count = subject_title.count("site:") if subject_title else 0
    
    if site_count > 3:
        filter_category = "toolbar_search_general"
    elif "music.youtube.com" in url:
        filter_category = "toolbar_search_youtube_music"
    elif "youtube.com" in url:
        filter_category = "toolbar_search_youtube"        
    elif "flickr.com" in url:
        filter_category = "toolbar_search_flickr"
    elif "maps.google.com" in url:
        filter_category = "toolbar_search_gmaps"
    elif "google.com/maps" in url:
        filter_category = "toolbar_search_gmaps"
    elif "earth.google.com" in url:
        filter_category = "toolbar_search_earth"
    elif "google.com/earth" in url:
        filter_category = "toolbar_search_earth"        
    elif "wikipedia.org" in url:
        filter_category = "toolbar_search_wikipedia"
    elif "wikimedia.org" in url:
        filter_category = "toolbar_search_wikimedia"
    else:
        filter_category = "toolbar_search_general"

    for icon in icon_data:
        if icon['filterCategory'] == filter_category:
            return icon.get('src', "")
    return ""

def get_label_from_url(url):
    url_lower = url.lower()
    if 'earth.google.com' in url_lower or 'google.com/earth' in url_lower:
        return 'Google Earth'
    elif 'flickr.com' in url_lower:
        return 'Flickr'
    elif 'youtube.com' in url_lower:
        return 'YouTube'
    elif 'maps.google.com' in url_lower or 'google.com/maps' in url_lower:
        return 'Google Maps'
    elif 'google.com' in url_lower:
        return 'Google'
    elif 'wikipedia.org' in url_lower:
        return 'Wikipedia'
    elif 'wikimedia.org' in url_lower:
        return 'Wikimedia'
    else:
        return None

def format_history_entry(entry, icon_data):
    #logMsg(f'Formatting history entry for {entry["url"]}')
    url_id = generate_url_id(entry['url'])
    subject_id = generate_url_id(entry['title']) if entry['title'] else url_id
    thumbnail = get_default_img(entry['url'], icon_data, entry['title'])
    
    title_exists = bool(entry['title'] and entry['title'].strip())
    label_from_url = get_label_from_url(entry['url'])
    
    # Determine subject_title
    if title_exists:
        subject_title = entry['title'].split("site:")[0]
    else:
        if label_from_url:
            subject_title = label_from_url
        else:
            subject_title = entry['url']
    
    # Add img tag to subject_title if a thumbnail is found
    subject_icon = get_insight_src_icon(entry['url'], icon_data, entry['title'])
    logMsg(f'subject_icon: {subject_icon}')
    
    if thumbnail != "/data/images/full_size/web_history/default.jpg":
        subject_title = f"<span class='related-search-topic'><img class='related-topic-img' src='{subject_icon}' alt='{subject_title}'> {subject_title}</span>"
    
    # Determine content_name
    if title_exists:
        content_name = entry['title']
    else:
        if label_from_url:
            content_name = label_from_url
        else:
            content_name = entry['url'][:150]
    
    # Determine content
    if title_exists:
        content = entry['title']
    else:
        if label_from_url:
            content = label_from_url
        else:
            content = entry['url']
    
    # Determine description
    if title_exists:
        description = entry['title']
    else:
        if label_from_url:
            description = label_from_url
        else:
            description = entry['url']
    
    formatted_entry = {
        "insight_details": {
            "url_id": url_id,
            "subject_id": subject_id,
            "subject_title": subject_title,
            "data_category": "web_history",
            "data_category_id": generate_url_id("web_history"),
            "data_subject": "web_history",
            "data_subject_id": generate_url_id("web_history"),
            "content_name": content_name,
            "insight_src_icon": subject_icon
        },
        "default_img": thumbnail,
        "text_block": {
            "content": content,
            "description": description
        },
        "media_link": entry['url']
    }
    return formatted_entry

def save_history_to_json(history, file_path, icon_data):
    logMsg(f'Saving history to JSON file {file_path}')
    formatted_history = [format_history_entry(entry, icon_data) for entry in history]
    
    # Deduplicate entries by default_img
    unique_history = list({entry['default_img']: entry for entry in formatted_history}.values())
    
    # Limit to the most recent 150 entries
    limited_history = unique_history[:100]
    
    with open(file_path, 'w') as f:
        json.dump(limited_history, f, indent=4)


def archive_existing_file(file_path, archive_dir):
    logMsg(f'Archiving existing file {file_path}')
    if os.path.exists(file_path):
        archive_file_path = os.path.join(archive_dir, f"{os.path.basename(file_path)}_{TIMESTAMP}")
        shutil.move(file_path, archive_file_path)

def create_condensed_history(history):
    logMsg('Creating condensed history')
    return [entry for entry in history if not entry["url"].startswith("http://localhost")]

def main():
    global NODEJS_DATA  # Indicate that you're referring to the global variable
    logMsg(f"MAIN0 NODEJS_DATA: {NODEJS_DATA}")
    logMsg(f"Current Working Directory: {os.getcwd()}")
    logMsg(f"MAIN ICON_DATA_PATH: {ICON_DATA_PATH}")

    # Ensure directories exist
    os.makedirs(RPT_ARCHIVE_DIR, exist_ok=True)
    os.makedirs(RPT_DATA_OUT_FOLDER, exist_ok=True)
    os.makedirs(APP_ARCHIVE_DIR, exist_ok=True)
    os.makedirs(APP_DATA_OUT_FOLDER, exist_ok=True)
    
    # Archive existing files
    archive_existing_file(RPT_DATA_FULL_HIST, RPT_ARCHIVE_DIR)
    archive_existing_file(RPT_DATA_CONDENSED_HIST, RPT_ARCHIVE_DIR)
    archive_existing_file(APP_DATA_CONDENSED_HIST, APP_ARCHIVE_DIR)
    
    # Copy the database file to avoid locking issues
    copy_history_db(CHROME_APP_HIST_PATH, CHROMHIST_DB_COPY)
    
    # Fetch history from the copied database
    history = fetch_history_from_copy(CHROMHIST_DB_COPY)
    
    # Load icon data
    icon_data = load_icon_data()
    
    # Save full history to JSON
    logMsg('Saving full history to JSON')
    save_history_to_json(history, RPT_DATA_FULL_HIST, icon_data)
    
    # Create and save condensed history to JSON
    logMsg('Creating and saving condensed history to JSON')
    condensed_history = create_condensed_history(history)
    save_history_to_json(condensed_history, RPT_DATA_CONDENSED_HIST, icon_data)
    
    # Copy condensed history to APP_DATA
    logMsg('Copying condensed history to APP_DATA')
    shutil.copy2(RPT_DATA_CONDENSED_HIST, APP_DATA_CONDENSED_HIST)
    
    # Clean up the copied database file
    os.remove(CHROMHIST_DB_COPY)
    
    logMsg(f"Full history saved to {RPT_DATA_FULL_HIST}")
    logMsg(f"Condensed history saved to {RPT_DATA_CONDENSED_HIST}")
    logMsg(f"Condensed history copied to {APP_DATA_CONDENSED_HIST}")

if __name__ == "__main__":
    main()

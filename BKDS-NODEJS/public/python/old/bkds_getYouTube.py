"""
BKDS YouTube Video Search and Processing

This program searches YouTube for videos related to a given subject, processes the retrieved videos, and saves the results in a JSON file. The main steps include:

1. Define the search parameters: The program specifies search parameters for YouTube API, including keyword, video duration, order, and the number of results to fetch.
2. Search YouTube: It sends API requests to search YouTube videos based on the specified parameters. Videos are retrieved both by date and rating.
3. Process video data: The program extracts relevant information from the retrieved videos, such as title, description, thumbnail, URL, and timestamp.
4. Generate insight ID: It generates a unique hash based on the search term, video URL, and category to identify each insight.
5. Read JSON data: The program reads JSON data from a specified file containing subject information, including keywords and categories.
6. Process each keyword: It processes each keyword from the JSON data, searches for related YouTube videos, and generates insights for them.
7. Save output: The program replaces special characters and spaces in the category, saves the processed data to a JSON file with a timestamp, and creates the output file.

Usage:
python script.py

Ensure that you have the required API key set in the `api_key` variable.
"""

import requests
import os
from datetime import datetime
import json
import time
import hashlib
import argparse
import re
import sys
from bkdsLogMsg import log_msg

bkds_util_python = os.environ.get('BKDS_UTIL_PYTHON')
# Check if the environment variable is set
if bkds_util_python:
    print("set BKDS_UTIL_PYTHON ")
    # Append the directory path to sys.path
    sys.path.append(bkds_util_python)
else:
    # Handle the case where the environment variable is not set
    print("BKDS_UTIL_PYTHON environment variable is not set.")

#####################################################################
# Main Setup / Variables
    
subj_dir='BKDS_NODEJS_SUBJGEN'
out_dir = os.getenv(subj_dir)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("json_filepath", help="Path to the JSON file containing data to process")
    
    # Parse the command-line arguments
    return parser.parse_args()


# Parse command-line arguments
args = parse_arguments()
batch_id=args.batch_id
json_filepath = args.json_filepath
subjType='youtube'
output_prefix='bkds_subj_gen'
output_type='json'
api_key = "AIzaSyDcgsGziLZW504z2dXBvK9GH6NBePNsu4k"

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_GET_YOUTUBE', msg)
    print(msg)

def search_youtube(keyword, api_key):
    logMsg(f"getting search_youtube: {keyword}")
    """
    Search YouTube for videos related to a keyword. 
    Fetches 3 videos sorted by date and 3 videos sorted by rating.
    Each set of videos has a minimum length requirement.
    """
    base_url = 'https://www.googleapis.com/youtube/v3/search'
    videos = []

    # Search for videos sorted by date, longer than 1 minute
    params = {
        'part': 'snippet',
        'q': keyword,
        'type': 'video',
        'videoDuration': 'long',
        'order': 'date',
        'maxResults': 3,
        'key': api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        videos.extend(response.json()['items'])

    # Search for videos sorted by rating, longer than 2 minutes
    params['order'] = 'rating'
    params['videoDuration'] = 'medium'
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        videos.extend(response.json()['items'])

    # Remove duplicates and return the result
    seen = set()
    unique_videos = []
    for video in videos:
        if video['id']['videoId'] not in seen:
            unique_videos.append(video)
            seen.add(video['id']['videoId'])
    return unique_videos

def process_video_data(videos):
    logMsg(f"process_video_data: {videos}")
    """
    Extract relevant information from video data.
    """
    processed_videos = []
    for video in videos:
        video_data = {
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'thumbnail': video['snippet']['thumbnails']['high']['url'],
            'url': f'https://www.youtube.com/watch?v={video["id"]["videoId"]}',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        processed_videos.append(video_data)
    return processed_videos

def generate_insight_id(search_term, video_url, category):
    logMsg(f"generate_insight_id: {search_term}")
    """
    Generate a unique hash based on the concatenation of the search term, video URL, and category.
    """
    combined_string = f"{search_term}{video_url}{category}".encode('utf-8')[:100]
    return hashlib.sha256(combined_string).hexdigest()

def parse_arguments():
    logMsg(f"parse_arguments")
    parser = argparse.ArgumentParser(description="Process a subject")
    parser.add_argument("subj", help="Subject identifier")
    return parser.parse_args()

def main():
    logMsg(f"starting main")
    # Parse command-line arguments
    #args = parse_arguments()
    logMsg(f'using json_filepath and batch_id {json_filepath} for {batch_id}')


    # Read JSON data from the file
    with open(json_filepath, 'r') as file:
        json_data = json.load(file)

    output_data = []

    # Process each keyword
    for item in json_data:
        subjID = item['subj_id']
        entry = item['entry']  # Access the 'entry' dictionary
        keyword = entry['keyword']  # Get the 'keyword' from 'entry'
        category = entry['category']  # Get the 'category' from 'entry'
        logMsg(f'processing {keyword} for {category}')
            
        videos = search_youtube(keyword, api_key)
        logMsg(f'retrieved {videos} for {category}')
        
        processed_videos = process_video_data(videos)
        logMsg(f'processed video data')

        insightID = generate_insight_id(keyword, subjID, category)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logMsg(f'generated insight ID {insightID}')
        
        output_data.append({
            "searchTerm": keyword,
            "insightID": insightID,
            "subjID" : subjID,
            "category": category,
            "videos": processed_videos,
            "collection_date": timestamp
        })

        # Replace special characters and spaces with underscores in the category variable
        category_cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', category)
        category_cleaned = category_cleaned.replace(' ', '_')

        # Save the output data to a JSON file with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        keyword_cleaned = re.sub(r'[^a-zA-Z0-9_]+', '_', keyword).strip('_')

        output_filepath=os.path.join(out_dir,  f'{subjType}/{output_prefix}_{subjType}_{keyword_cleaned}_{subjID}_{timestamp}.{output_type}')
        output_filepath = output_filepath.replace('__', '_')
        print(f'writing output_filepath: {output_filepath}')

        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        with open(output_filepath, 'w') as file:
            json.dump(output_data, file, indent=4)
        
        time.sleep(3)


if __name__ == "__main__":
    main()

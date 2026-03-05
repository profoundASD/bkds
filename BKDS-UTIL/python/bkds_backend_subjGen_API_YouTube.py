"""
YouTube Data Processing Script

This script is designed for searching and processing YouTube videos based on given search terms. 
It utilizes the YouTube Data API to fetch videos, focusing on parameters like date, rating, and 
duration filters, and processes the retrieved data to extract essential details like titles, 
descriptions, thumbnails, URLs, and timestamps.

Features:
- Utilizes the YouTube Data API for searching videos with specified keywords.
- Processes video data to extract titles, descriptions, thumbnails, URLs, and timestamps.
- Supports sorting videos by date and rating with duration filters.
- Requires YouTube API key set as an environment variable for authentication.
- Incorporates robust logging for events and errors.

Usage:
- Set the YouTube API key as an environment variable ("YOUTUBE_API_KEY").
- Invoke the `getYouTubeData` function with a searchTerm to start the search process.

Dependencies:
- `requests` library for API requests.
- `datetime` library for timestamp handling.
- `bkdsUtilities` module for logging functionalities.

Important:
- Ensure the YouTube API key is correctly configured in the environment before execution.
"""

import requests
import sys
import os
from datetime import datetime
#custom functions
from bkds_Utilities import log_msg

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id='SUBJ_GEN_YOUTUBE_API'

API_KEY = os.getenv("YOUTUBE_API_KEY")
#API_KEY = 'AIzaSyBYRxfjRAlzKfIHwfn3vjn-x4YbhvD5AIU'
API_ENDPOINT='https://www.googleapis.com/youtube/v3/search'

########################################################################
#  Main logic and functions
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getVideoData(videos):
    logMsg(f"process_video_data: {videos}")
    """
    Extract relevant information from video data.
    """
    processed_videos = []
    for video in videos:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        video_data = {
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'thumbnail': video['snippet']['thumbnails']['high']['url'],
            'url': f'https://www.youtube.com/watch?v={video["id"]["videoId"]}',
            'timestamp': timestamp # Corrected usage
        }
        processed_videos.append(video_data)
    return processed_videos

def getYouTubeData(searchTerm):

    if not API_KEY:
        logMsg('API key for YouTube is not set.')
        sys.exit(1)

    """
    Search YouTube for videos related to a searchTerm. 
    Fetches videos sorted by date and rating.
    Each set of videos has a minimum length requirement.
    """
    logMsg(f"Searching YouTube for: {searchTerm}")
    base_url = API_ENDPOINT
    videos = []

    # Search for videos sorted by date, longer than 1 minute
    params = {
        'part': 'snippet',
        'q': searchTerm,
        'type': 'video',
        'videoDuration': 'long',
        'order': 'date',
        'maxResults': 5,
        'key': API_KEY
    }
    response = requests.get(base_url, params=params)
    logMsg(f"response.status_code {response.status_code}")
    logMsg(f"response.json()['items'] {response.json()['items']}")
    if response.status_code == 200:
        videos.extend(response.json()['items'])
    # Search for videos sorted by rating, longer than 2 minutes
    params['order'] = 'rating'
    params['videoDuration'] = 'medium'
    response = requests.get(base_url, params=params)
    logMsg(f"response for: {response} for url {base_url} using {params}" )

    if response.status_code == 200:
        videos.extend(response.json()['items'])

    # Remove duplicates and return the result
    seen = set()
    unique_videos = []
    for video in videos:
        logMsg(f"processing_video {video}")
        if video['id']['videoId'] not in seen:
            unique_videos.append(video)
            seen.add(video['id']['videoId'])
    return unique_videos

"""
YouTube Channel Video Retrieval Script

This script is designed to fetch the latest videos from specified YouTube channels.
It utilizes the YouTube Data API to fetch videos based on channel usernames or IDs 
provided in a JSON configuration file. The number of videos to retrieve is also 
specified in the config file.

Features:
- Utilizes the YouTube Data API for fetching the latest videos from channels.
- Processes video data to extract titles, descriptions, thumbnails, URLs, and timestamps.
- Supports dynamic configuration of channels and number of videos.
- Requires YouTube API key set as an environment variable for authentication.
- Incorporates robust logging for events and errors.

Usage:
- Set the YouTube API key as an environment variable ("YOUTUBE_API_KEY").
- Place the JSON configuration file (`config.json`) in the same directory as the script.
- Invoke the script to start the video retrieval process.

Dependencies:
- `requests` library for API requests.
- `datetime` library for timestamp handling.
- `json` library for handling the configuration file.
- `bkdsUtilities` module for logging functionalities.

Important:
- Ensure the YouTube API key is correctly configured in the environment before execution.
"""

import requests
import sys
import os
import json
import argparse
from datetime import datetime, timedelta

# custom functions
from bkds_Utilities import log_msg

def parse_arguments():
    parser = argparse.ArgumentParser(description="Aggregate rocket launch data and generate a consolidated output JSON file.")
    parser.add_argument("batch_id", help="Batch ID for the current run")
    return parser.parse_args()

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

args = parse_arguments()
batch_id = args.batch_id

API_KEY = os.getenv("YOUTUBE_API_KEY")
API_ENDPOINT_CHANNEL = 'https://www.googleapis.com/youtube/v3/channels'
API_ENDPOINT_PLAYLIST_ITEMS = 'https://www.googleapis.com/youtube/v3/playlistItems'

util_data = os.getenv('BKDS_UTIL_DATA')
util_config_data = os.path.join(util_data, 'config')
video_data = os.getenv('BKDS_NODEJS_DATA')
video_index_out = os.path.join(video_data, 'content_feeds', 'rockets', 'launches', 'bkds_yt_launches.json')

CONFIG_FILE = os.path.join(util_config_data, 'bkds_yt_channelData.json')

########################################################################
# Main logic and functions
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def load_existing_videos():
    logMsg("load_existing_videos()")
    if os.path.exists(video_index_out):
        with open(video_index_out, 'r') as file:
            return json.load(file)
    return []

def save_videos(videos):
    logMsg("save_videos()")
    existing_videos = load_existing_videos()
    existing_video_ids = {video['url'] for video in existing_videos}
    
    new_videos = [video for video in videos if video['url'] not in existing_video_ids]
    
    if new_videos:
        existing_videos.extend(new_videos)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(video_index_out), exist_ok=True)
        with open(video_index_out, 'w') as file:
            json.dump(existing_videos, file, indent=4)

def get_file_timestamp():
    if os.path.exists(video_index_out):
        return datetime.fromtimestamp(os.path.getmtime(video_index_out))
    return None

def getVideoData(videos):
    logMsg("getVidoeData()")
    """
    Extract relevant information from video data.
    """
    #logMsg(f"process_video_data: {videos}")
    processed_videos = []
    for video in videos:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        video_data = {
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'thumbnail': video['snippet']['thumbnails']['high']['url'],
            'url': f'https://www.youtube.com/watch?v={video["snippet"]["resourceId"]["videoId"]}',
            'timestamp': timestamp
        }
        processed_videos.append(video_data)
    return processed_videos

def getChannelIdByUsername(username):
    logMsg(f"getChannelIdByUsername with username {username}")
    """
    Fetch the channel ID using the channel username.
    """
    #logMsg(f"Fetching channel ID for username: {username}")
    params = {
        'part': 'id',
        'forUsername': username,
        'key': API_KEY
    }
    response = requests.get(API_ENDPOINT_CHANNEL, params=params)
    logMsg(f"response.status_code {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['id']
        else:
            logMsg(f"No channel found for username: {username}")
            sys.exit(1)
    else:
        logMsg(f"Error fetching data from YouTube API: {response.text}")
        sys.exit(1)

def getUploadsPlaylistId(channelId):
    logMsg(f"getUploadsPlaylistId with channelId {channelId} and API_KEY {API_KEY}")
    """
    Get the uploads playlist ID for the channel.
    """
    #logMsg(f"Fetching uploads playlist ID for channel ID: {channelId}")
    params = {
        'part': 'contentDetails',
        'id': channelId,
        'key': API_KEY
    }
    response = requests.get(API_ENDPOINT_CHANNEL, params=params)
    #logMsg(f"response.status_code {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        else:
            logMsg(f"No content details found for channel ID: {channelId}")
            sys.exit(1)
    else:
        logMsg(f"Error fetching data from YouTube API: {response.text}")
        sys.exit(1)

def getYouTubeChannelVideos(uploadsPlaylistId, num_vids):
    logMsg(f"getYouTubeChannelVideos with uploadsPlaylistId {uploadsPlaylistId} and num_Vids: {num_vids}")
    logMsg(f"getYouTubeChannelVideos with uploadsPlaylistId using {API_KEY}")
    """
    Fetch the latest videos from a YouTube channel's uploads playlist.
    """
    if not API_KEY:
        logMsg('API key for YouTube is not set.')
        sys.exit(1)

    #logMsg(f"Fetching latest {num_vids} videos from uploads playlist ID: {uploadsPlaylistId}")
    videos = []

    params = {
        'part': 'snippet',
        'playlistId': uploadsPlaylistId,
        'maxResults': num_vids,
        'key': API_KEY
    }

    response = requests.get(API_ENDPOINT_PLAYLIST_ITEMS, params=params)
    #logMsg(f"response.status_code {response.status_code}")

    if response.status_code == 200:
        videos = response.json()['items']
    else:
        logMsg(f"Error fetching data from YouTube API: {response.text}")
        sys.exit(1)

    return videos

def main():
    # Check the timestamp of the video index out file
    file_timestamp = get_file_timestamp()
    if file_timestamp and datetime.utcnow() - file_timestamp < timedelta(hours=24):
        logMsg("File was updated within the last 24 hours. Exiting.")
        return

    # Load configuration
    if not os.path.exists(CONFIG_FILE):
        logMsg(f"Configuration file {CONFIG_FILE} not found.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)

    all_videos = []

    # Process each channel in the configuration file
    for entry in config:
        url_or_username = entry['id']
        num_vids = entry['num_vids']

        if url_or_username.startswith('@'):
            # Remove the '@' symbol to get the username
            username = url_or_username[1:]
            channel_id = getChannelIdByUsername(username)
        else:
            channel_id = url_or_username

        uploads_playlist_id = getUploadsPlaylistId(channel_id)
        videos = getYouTubeChannelVideos(uploads_playlist_id, num_vids)
        processed_videos = getVideoData(videos)
        all_videos.extend(processed_videos)

    # Save new videos to the index out file
    save_videos(all_videos)

if __name__ == "__main__":
    main()

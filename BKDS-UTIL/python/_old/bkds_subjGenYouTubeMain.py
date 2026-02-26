"""
YouTube Video Processing and Data Generation Script

This script processes data from YouTube based on input obtained from a JSON file. It is designed 
to handle the extraction and processing of YouTube video data related to specified search terms, 
gathering comprehensive details about each video.

Features:
- Reads input data (search terms and related information) from a specified JSON file.
- Utilizes YouTube API to search for videos corresponding to each search term.
- Processes retrieved video data to extract key information like titles, URLs, and other metadata.
- Generates unique identifiers for each processed video for data tracking and management.
- Saves processed data in a specified format to an output file.
- Ensures avoidance of duplicate processing for the same search term.

Usage:
- The script expects a JSON file path containing search terms and associated data.
- Output data is saved in a specified format (e.g., JSON, CSV) with a given file name prefix.
- The script is designed to be used with the 'YouTube' subject type.

Note:
- The script includes sleep intervals (defined by 'api_wait') between API requests to manage request rate limits.
- Proper error handling and logging are implemented for traceability and debugging.
"""
import json
from datetime import datetime
import time
import os
#custom functions
from bkds_subjGenYouTubeAPI import getYouTubeData, getVideoData
from bkdsUtilities import genInsightID, log_msg, subjGenOutputHandler, fetch_data

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id='SUBJ_GEN_YOUTUBE_MAIN'

rec_key='record_id'
search_key='search_id'
category_key='category'
search_term_key='search_term'

api_wait = 3
########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def subjGenYouTube(sql_query, output_prefix, output_type, subjType):
    data = fetch_data(sql_query)  # Fetch data using the SQL query

    output_data = []
    processed_terms = set()

    for item in data:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        insightID = item[rec_key]
        searchTerm = item[search_term_key]
        searchID = item[search_key]
        category = item[category_key]
        logMsg(f'Processing {searchTerm} for {category}')

        if searchTerm not in processed_terms:
            videos = getYouTubeData(searchTerm)
            processed_videos = getVideoData(videos)
            resultID = genInsightID(searchTerm, insightID, timestamp)
            result_item = {
                "searchID" : searchID,
                "resultID" : resultID,
                "insightID": insightID,
                "videos": processed_videos,
                "category": category,
                "utcTime": timestamp
            }
            output_data.append(result_item)
            processed_terms.add(searchTerm)

        # Use subjGenOutputHandler from bkdsUtilities for file handling
        output_filepath = subjGenOutputHandler(output_data, subjType, output_prefix, output_type, searchTerm, insightID, timestamp)
        logMsg(f"Results output: {output_filepath}")
        time.sleep(api_wait)

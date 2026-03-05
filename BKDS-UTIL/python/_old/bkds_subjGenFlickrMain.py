"""
Flickr Subject Generation Script

This script processes a JSON file containing searchTerms for Flickr image searches, fetches relevant 
images using the Flickr API, and organizes the data into a structured format. 
It is designed to handle multiple searchTerms, avoid redundant searches, and compile the results 
with detailed insights.

Features:
- Reads searchTerms from a JSON file for Flickr image searches.
- Utilizes Flickr API to fetch images based on the provided searchTerms.
- Generates unique insight IDs for each searchTerm.
- Compiles key information about fetched images, such as URLs, in a structured output.
- Saves the processed data in a specified format with a timestamped filename.
- Supports configurable output prefix and file type.
- Implements an interval delay between processing each searchTerm for efficient API usage.
- Logs processing steps and errors for traceability.

Usage:
- Execute `subjGenFlickr` with the path to a JSON file, output prefix, output type, and subject type ('flickr').
"""

from datetime import datetime
import time
import os
#custom functions
from bkds_subjGenFlickrAPI import getFlickrData
from bkdsUtilities import genInsightID, log_msg, subjGenOutputHandler, fetch_data

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id='SUBJ_GEN_FLICKR_MAIN'

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

def subjGenFlickr(sql_query, output_prefix, output_type, subjType):
    data = fetch_data(sql_query)  # Fetch data using the SQL query

    output_data = []
    processed_terms = set()

    for item in data:
        logMsg(f'processing {item}')
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        insightID = item[rec_key]
        searchTerm = item[search_term_key]
        searchID = item[search_key]
        category = item[category_key]
        
        logMsg(f'processing {searchTerm} for {category}')

        if searchTerm not in processed_terms:
            images = getFlickrData(searchTerm, 10)
            resultID = genInsightID(searchTerm, insightID, timestamp)
            result_item = {
                "searchID" : searchID,
                "resultID" : resultID,
                "insightID": insightID,
                "category": category,
                "searchTerm": searchTerm,
                "Images": images,
                "category": category,
                "utcTime": timestamp
            }
            output_data.append(result_item)
            processed_terms.add(searchTerm)

        output_filepath = subjGenOutputHandler(output_data, subjType, output_prefix, output_type, searchTerm, insightID, timestamp)
        logMsg(f"Results output: {output_filepath}")
        time.sleep(api_wait)

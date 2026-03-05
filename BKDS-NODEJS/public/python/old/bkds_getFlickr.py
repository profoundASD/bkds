"""
BKDS Flickr Image Search and Processing

This program searches Flickr for images related to a given subject, processes the retrieved images, and saves the results in a JSON file. The main steps include:

1. Flickr API Configuration: The program configures the Flickr API key and defines parameters for searching images on Flickr.
2. Search Flickr Images: It sends API requests to search Flickr for images based on the specified search term and additional filters.
3. Read JSON Data: The program reads search terms from a JSON file containing subject information, including keywords, types, and categories.
4. Process Each Keyword: It iterates over each keyword from the JSON data, checks if it has been processed before, searches Flickr for related images, and collects relevant information.
5. Save Output: The program defines the output filename format, saves the processed data to a JSON file with a timestamp, and prints the output filename for reference.

Usage:
- Replace `FLICKR_API_KEY` with your Flickr API key.
- Ensure that you have a valid JSON file (`bkds_river_subj.json`) with subject information in the specified input path.

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

#custom functions
bkds_util_python = os.environ.get('BKDS_UTIL_PYTHON')
# Check if the environment variable is set
if bkds_util_python:
    print("set BKDS_UTIL_PYTHON ")
    # Append the directory path to sys.path
    sys.path.append(bkds_util_python)
else:
    # Handle the case where the environment variable is not set
    print("BKDS_UTIL_PYTHON environment variable is not set.")
from bkdsUtilities import logMsg

#####################################################################
# Main Setup / Variables
    
subj_dir='BKDS_NODEJS_SUBJGEN'
out_dir = os.getenv(subj_dir)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("json_filepath", help="Path to the JSON file containing data to process")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    json_filepath = args.json_filepath
    return parser.parse_args()


# Parse command-line arguments
args = parse_arguments()
batch_id=args.batch_id
json_filepath = args.json_filepath
subjType='flickr'
output_prefix='bkds_subj_gen'
output_type='json'
FLICKR_API_KEY = "d46b9056b686756084e405fa5a510177"

########################################################################
#  Main logic and functions
# Replace with your Flickr API key


# Function to search for images on Flickr with additional filters
def search_flickr_images(keyword, num_images):
    print(f"Searching Flickr for: {keyword}")
    base_url = "https://www.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": FLICKR_API_KEY,
        "format": "json",
        "nojsoncallback": 1,
        "text": keyword,
        "per_page": num_images,
        "license": "1,2,3,4,5,6,7",  # Creative Commons licenses
        "safe_search": 1,  # Filter for safe content
        "content_type": 1,  # Photos only (no screenshots or artwork)
        "people": "0",  # Exclude photos with people
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "photos" in data:
            photos = data["photos"]["photo"]
            image_urls = [f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}.jpg" for photo in photos]
            return image_urls
    except Exception as e:
        print(f"Error searching Flickr for '{keyword}': {str(e)}")

    return []

def generate_insight_id(search_term, string_id, category):
    logMsg(f"generate_insight_id: {search_term}")
    """
    Generate a unique hash based on the concatenation of the search term,  URL, and category.
    """
    combined_string = f"{search_term}{string_id}{category}".encode('utf-8')[:100]
    return hashlib.sha256(combined_string).hexdigest()

def main():
    print("Starting main...")
    # Read JSON data from the file
    with open(json_filepath, 'r') as file:
        json_data = json.load(file)

    output_data = []
    processed_terms = set()


    # Iterate over each JSON entry
    for item in json_data:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        subjID = item['subj_id']
        entry = item['entry'] 
        keyword = entry['keyword']  
        category = entry['category']
        logMsg(f'processing {keyword} for {category}')
        if keyword in processed_terms:
            print(f"Skipping '{keyword}' as it has already been processed.")
            continue

        time.sleep(4)
        images = search_flickr_images(keyword, 10)
        insightID = generate_insight_id(keyword, subjID, category)

        result_item = {
            "searchTerm": keyword,
            "insightID": insightID,
            "subjID" : subjID,
            "Images": images,
            "category": category,
            "collection_date": timestamp
        }

        output_data.append(result_item)


        # Replace special characters and spaces with underscores in the category variable
        category_cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', category)
        category_cleaned = category_cleaned.replace(' ', '_')
        keyword_cleaned = re.sub(r'[^a-zA-Z0-9_]+', '_', keyword).strip('_')
        
        output_filepath=os.path.join(out_dir,  f'{subjType}/{output_prefix}_{subjType}_{keyword_cleaned}_{subjID}_{timestamp}.{output_type}')
        output_filepath = output_filepath.replace('__', '_')
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        # Write the result_data to the JSON file
        with open(output_filepath, 'w') as output_file:
            json.dump(output_data, output_file, indent=4)

        # Print the output filename for reference
        print(f"Saved results to {output_filepath}")

if __name__ == "__main__":
    main()

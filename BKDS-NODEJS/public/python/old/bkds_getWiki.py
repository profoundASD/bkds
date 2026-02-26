"""
Get Wikipedia Images and Metadata

This program processes a JSON file containing data to fetch Wikipedia images and metadata based on search keywords. It performs the following steps:

1. Parse command-line arguments: The program accepts batch ID, node ID, and a JSON file path as input arguments.
2. Read JSON data: The program reads data from the specified JSON file, which contains information about keywords, categories, and subject IDs.
3. Process data: For each item in the JSON data, the program checks if it contains an 'entry' dictionary with a 'keyword' key. If found, it searches Wikipedia for the keyword and fetches metadata, including search results, images, and page extracts.
4. Generate Insight IDs: The program generates a unique hash (Insight ID) based on the search term, page URL, category, and a random number.
5. Save results: The program saves the fetched data, including search results, images, and metadata, to individual JSON files with timestamps and cleaned category and keyword names.
6. Log messages: Throughout the process, the program logs messages, including status updates and errors.

Usage:
python script.py <batch_id> <json_filepath>

Arguments:
- batch_id: The batch ID for processing.
- json_filepath: The path to the JSON file containing data to process.

Example:
python script.py 1234 NODE1 /path/to/data.json
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
import socket
import random
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
hostname = socket.gethostname()

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
subjType='wiki'
output_prefix='bkds_subj_gen'
output_type='json'

########################################################################
#  Main logic and functions


def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_GET_WIKI', msg)
    print(msg)
    
def get_page_extract(title):
    logMsg(f"gettin gpage extract for title: {title}")
    """
    Get the page summary (extract) for a given Wikipedia page title.
    """
    API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        pages = response.json().get('query', {}).get('pages', {})

        for page_id, page in pages.items():
            if 'extract' in page:
                return page['extract']

    except requests.RequestException as e:
        return None  # Return None in case of any error


def search_wikipedia(keyword):
    logMsg(f"Searching wikipedia for keyword= {keyword}")
    """
    Search Wikipedia for a given keyword and return the titles and URLs of the top results.
    """
    API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'list': 'search',
        'format': 'json',
        'utf8': '1',
        'formatversion': '2',
        'srsearch': keyword
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        search_results = response.json().get('query', {}).get('search', [])[:3]
        return [{'title': result['title'], 'wiki_url': f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"} for result in search_results]
    except requests.RequestException as e:
        return []  # Return an empty list in case of any error

import requests

def get_images_from_page(title):
    logMsg(f"get images from page title: {title}")
    """
    Get all image URLs from a given Wikipedia page title and filter them to the first 10 valid images.
    """
    API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'images',
        'format': 'json',
        'imlimit': 'max'  # Retrieve all images without limiting to 20
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        pages = response.json().get('query', {}).get('pages', {})

        image_titles = []
        for page_id, page in pages.items():
            if 'images' in page:
                image_titles = [img['title'] for img in page['images']]
                break

        valid_image_urls = []

        for title in image_titles:
            image_url = get_image_url(title)
            if image_url and is_valid_image(image_url, title):
                valid_image_urls.append(image_url)

                # Break the loop if we have collected 10 valid images
                if len(valid_image_urls) >= 10:
                    break

        return valid_image_urls
    except requests.RequestException as e:
        return []  # Return an empty list in case of any error


def is_valid_image(image_url, image_title):
    """
    Apply filter rules to determine if the image is valid based on its URL and title.
    """
    upper_url = image_url.upper()
    upper_title = image_title.upper()

    # Filter based on file type and URL contents
    if ( (upper_title.endswith('.PNG') 
          or  upper_title.endswith('.JPG') 
          or  upper_title.endswith('.JPEG') 
          or  upper_title.endswith('.GIF')
          ) 
          and 
        "PROTECTED" not in upper_url and
        "PROTECTION" not in upper_url and
        "PENDING" not in upper_url and
        "FEATURED" not in upper_url and
        "LISTEN" not in upper_url and
        "SYMBOL" not in upper_url and
        "QUESTION_BOOK" not in upper_url and
        "WIKI_LETTER" not in upper_url and
        "TEXT_DOCUMENT" not in upper_url and
        "QUESTION_MARK" not in upper_url and
        "EMBLEM-MONEY" not in upper_url and
        "ICON" not in upper_url and
        "RED_PENCIL" not in upper_url):
        return True

    return False
def get_image_url(image_title):
    logMsg(f"checking image: url/title = {image_title}")
    """f
    Get the URL of an image from its title on Wikipedia and apply filters.
    """
    API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'titles': image_title,
        'prop': 'imageinfo',
        'iiprop': 'url',
        'format': 'json'
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        pages = response.json().get('query', {}).get('pages', {})

        for page_id, page in pages.items():
            if 'imageinfo' in page:
                image_url = page['imageinfo'][0]['url']
                if is_valid_image(image_url, image_title):
                    return image_url
    except requests.RequestException as e:
        return None  # Return None in case of any error

def generate_insight_id(search_term, page_url, category):
    logMsg(f"generating insight ID: search_term/url/category = {search_term}, {page_url}, {category}")
    """
    Generate a unique hash based on the concatenation of the first 100 bytes of 
    the search term, page URL, and category, along with a random number.
    """
    combined_string = f"{search_term}{page_url}{category}".encode('utf-8')[:100]
    
    # Generate a random number between 1 and 10000 (adjust as needed)
    random_number = random.randint(1, 10000)
    # Append the random number to the combined string
    combined_string += str(random_number).encode('utf-8')
    # Calculate the hash
    hash_value = hashlib.sha256(combined_string).hexdigest()
    
    return hash_value

def main():
    logMsg('bkds_GetWiki main')

    logMsg(f"Processing JSON data from file: {json_filepath}")

    # Read JSON data from the specified file
    with open(json_filepath, 'r') as file:
        json_data = json.load(file)
    logMsg(f'json_filepath{json_filepath}')
    for item in json_data:
        current_output_data=[]
        # Check if the 'filePath' key exists in the item
        # Check if the 'entry' dictionary exists in the item
        if 'entry' in item:
            entry_data = item['entry']
            subjID=item['subj_id']
            # Check if the 'keyword' key exists in the 'entry' dictionary
            if 'keyword' in entry_data:
                keyword_to_process = entry_data['keyword']
                # Here you can add the code to process each file
                # For example, reading the file:
                try:
                    logMsg(f"Processing file: {keyword_to_process}")

                    print(f'keyword: {keyword_to_process}')

                    time.sleep(2)
                    search_results = search_wikipedia(keyword_to_process)
                    print(f'search_results: {search_results}')

                    for result in search_results:
                        logMsg(f'wiki result: {result}')

                        category = item.get('category', '')
                        subj_url = result.get('wiki_url', '')
                        page_title = result.get('title', '')

                        images = get_images_from_page(page_title)
                        time.sleep(2)
                        extract = get_page_extract(page_title)
                        logMsg(f'wiki images: {images}')
                        # logMsg(f'wiki extract: {extract}')

                        insightID = item.get('subjID', '')
                        insightSearchID = generate_insight_id(keyword_to_process, subj_url, category)

                        current_output_data.append({
                            "searchTerm": keyword_to_process,
                            "insightID": insightID,
                            "insightSearchID": insightSearchID,
                            "category": category,
                            "pageURL": subj_url,
                            "images": images,
                            "extract": extract,
                            "subjTitle": page_title
                        })

                    # Save the output data to a JSON file with a timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    keyword_cleaned = re.sub(r'[^a-zA-Z0-9_]+', '_', keyword_to_process).strip('_')

                    output_filepath=os.path.join(out_dir,  f'{subjType}/{output_prefix}_{subjType}_{keyword_cleaned}_{subjID}_{timestamp}.{output_type}')
                    output_filepath = output_filepath.replace('__', '_')
                    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                    with open(output_filepath, 'w') as output_file:
                        json.dump(current_output_data, output_file, indent=4)

                except FileNotFoundError:
                    logMsg(f"File not found: {keyword_to_process}")
                except json.JSONDecodeError:
                    logMsg(f"Invalid JSON in file: {keyword_to_process}")
                except Exception as e:
                    logMsg(f"Error processing file {keyword_to_process}: {e}")

        else:
            logMsg("File path key ('filePath') not found in JSON entry.")


        

if __name__ == "__main__":
    main()
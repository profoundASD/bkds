import requests
import sys
import os
from datetime import datetime
import time
# Custom functions
from bkds_Utilities import log_msg, isValidImage, genInsightID
"""
Script: Wikipedia Data Retrieval
Description:
    This script is designed to interact with the Wikipedia API to fetch various types of data. It includes functions to search Wikipedia for specific terms, retrieve page summaries (extracts), and fetch image URLs from Wikipedia pages. The script is structured to facilitate the extraction and processing of Wikipedia data for further analysis or storage.

Usage:
    - Execute the script with a specified search term to initiate the data retrieval process.
    - The script calls various functions to interact with the Wikipedia API, such as:
        - searchWiki(searchTerm): Searches Wikipedia for the given term and returns titles and URLs.
        - getPageExtract(title): Retrieves the summary of a given Wikipedia page.
        - getPageImages(title): Fetches image URLs from the specified Wikipedia page.
        - getImageURL(image_title): Retrieves the URL of a specific image from Wikipedia.
        - getWikiData(searchTerm): Orchestrates the process of fetching comprehensive data (including images and extracts) for a given search term.

Notes:
    - The script utilizes a batching mechanism (defined by 'batch_id') for processing.
    - API wait times and data limits are configurable.
    - Error handling is implemented for API requests.
"""

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id='SUBJ_GEN_WIKI_API'

#wiki API setup
API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
inLimit='max'

envPath = os.environ.get('BKDS_UTIL_PYTHON')
sys.path.append(envPath)

#wiki api data keys
query_key='query'
pages_key='pages'
images_key='images'
imageinfo_key='imageinfo'
url_key='url'
out_type='json'
search_key='search'
text_key='extract' #page summary index
title_key='title'
category_key='category'

rec_key='record_id'
search_term_key='search_term'

extract_prop='extracts' #page summary prop
api_wait=5
########################################################################
# Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)


def searchWiki(searchTerm):
    logMsg(f"starting searchWiki with: {searchTerm}")
    """
    Search Wikipedia for a given searchTerm and return the titles and URLs of the top results.
    """
    params = {
        'action': query_key,
        'list': search_key,
        'format': out_type,
        'srsearch': searchTerm,
        'utf8': '1',
        'formatversion': '2'
    }
    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        #search_results = response.json().get(query_key, {}).get(search_key, [])[:3]
        search_results = response.json().get('query', {}).get('search', [])[:3]
        return [{'title': result['title'], 'wiki_url': f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"} for result in search_results]
    except requests.RequestException as e:
        logMsg(f"Error searching Wikipedia: {e}")
        return []

def getPageExtract(title):
    """
    Get the page summary (extract) for a given Wikipedia page title.
    """
    logMsg(f"getPageExtract for title: {title}")
    params = {
        'action': query_key,
        'format': out_type,
        'titles': title,
        'prop': extract_prop,
        'exintro': True,
        'explaintext': True
    }
    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        pages = response.json().get(query_key, {}).get(pages_key, {})
        for page_id, page in pages.items():
            if text_key in page:
                logMsg(f"got extract for {page_id}")
                return page[text_key]
    except requests.RequestException as e:
        logMsg(f"Error fetching page extract: {e}")
        return None

def getPageImages(title):
    """
    Get all image URLs from a given Wikipedia page title.
    """
    logMsg(f"Getting images from page title: {title}")
    params = {
        'action': query_key,
        'titles': title,
        'prop': images_key,
        'format': out_type,
        'imlimit': inLimit
    }
    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        pages = response.json().get(query_key, {}).get(pages_key, {})
        image_titles = []
        for page_id, page in pages.items():
            #logMsg(f"getPageImages {page_id}")
            if images_key in page:
                logMsg(f"found images {page_id}: {page}")
                image_titles = [img[title_key] for img in page[images_key]]

        #valid_image_urls = [getImageURL(title) for title in image_titles if isValidImage(getImageURL(title), title)]
        valid_image_urls = [url for url in ## list comprehension to filter output
                    [getImageURL(title) for title in image_titles if isValidImage(getImageURL(title), title)] 
                    if url is not None and len(url) > 7]
        
        logMsg(f"valid urls\n{valid_image_urls[:10]}")
        return valid_image_urls[:10]  # Limiting to the first 10 valid images
    except requests.RequestException as e:
        logMsg(f"Error fetching images from page: {e}")
        return []

def getImageURL(image_title):
    """
    Retrieves the URL of an image from its title on Wikipedia.
    """
    params = {
        'action': query_key,
        'titles': image_title,
        'prop': imageinfo_key,
        'iiprop': 'url',
        'format': out_type
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        pages = response.json().get(query_key, {}).get(pages_key, {})

        for page_id, page in pages.items():
            if imageinfo_key in page:
                image_url = page[imageinfo_key][0]['url']
                #logMsg(f'checking image: {image_title}')
                return image_url
    except requests.RequestException as e:
        return None  # Return None in case of any error
    
def getWikiData(searchTerm):
    logMsg(f'started getWikiData from {program_name} with searchTerm {searchTerm} and search_key {search_key}')

    # Initialize an empty list to store all search results
    all_search_results = []
    logMsg(f'Using {search_key} in {searchTerm}')

    search_results = searchWiki(searchTerm)
    
    for result in search_results:
        pageTitle = result.get('title', '')
        searchURL = result.get('wiki_url', '')
        
        images = getPageImages(pageTitle)
        time.sleep(api_wait)
        extract = getPageExtract(pageTitle)

        resultID = genInsightID(searchTerm, searchURL, search_key)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create a dictionary for the current result
        current_result = {
            "wiki_result_id": resultID,
            "subjTitle": pageTitle,
            "pageURL": searchURL,
            "images": images,
            "extract": extract,
            "utcTime": timestamp
        }

        # Append the current result to the list
        all_search_results.append(current_result)

        time.sleep(api_wait)
 
    # Return the list of all search results
    return all_search_results
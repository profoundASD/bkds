import requests
import os
#custom functions
from bkds_Utilities import log_msg

"""
Script: Flickr Image Retrieval
Description:
    This script interacts with the Flickr API to search and retrieve image data. It enables fetching URLs of images related to a specified search term. The script utilizes various Flickr API parameters to refine the search and ensure the relevance and appropriateness of the results.

Usage:
    - Execute the script with a search term and desired search depth (number of images).
    - The script primarily uses the getFlickrData function to perform searches on Flickr.
    - Functions included:
        - getFlickrData(searchTerm, search_depth): Searches Flickr for images matching the searchTerm, limited by search_depth.

Configuration:
    - API_ENDPOINT: Base URL for Flickr's RESTful services.
    - API_KEY: Flickr API key, obtained from the environment variables.
    - API_METHOD: Method used for the Flickr API search.
    - API_LICENSE, MISC_FLAG1, ON_FLAG, OFF_FLAG: Various flags to customize the search behavior and results.
"""


#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id='SUBJ_GEN_FLICKR_API'

API_ENDPOINT = "https://www.flickr.com/services/rest/"
API_KEY=os.getenv("FLICKR_API_KEY")
API_METHOD="flickr.photos.search"
API_TYPE="json"
API_LICENSE="1,2,3,4,5,6,7"
MISC_FLAG1="0"
ON_FLAG=1
OFF_FLAG=0
img_url='https://live.staticflickr.com'

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getFlickrData(searchTerm, search_depth):
    """
    Searches Flickr for images related to a given searchTerm.

    :param searchTerm: The search term for the image search.
    :param search_depth: The number of images to retrieve.
    :param api_key: The API key for accessing Flickr services.
    :return: A list of URLs of the found images.
    """
    logMsg(f"starting getFlickrData for: {searchTerm}")
    base_url = API_ENDPOINT
    params = {
        "method": API_METHOD,
        "api_key": API_KEY,
        "format": API_TYPE,
        "nojsoncallback": ON_FLAG,
        "text": searchTerm,
        "per_page": search_depth,
        "license": API_LICENSE,  # Creative Commons licenses
        "safe_search": ON_FLAG,  # Filter for safe content
        "content_type": ON_FLAG,  # Photos only (no screenshots or artwork)
        "people": MISC_FLAG1,  # Exclude photos with people
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "photos" in data:
            photos = data["photos"]["photo"]
            image_urls = [
                f"{img_url}/{photo['server']}/{photo['id']}_{photo['secret']}.jpg" 
                for photo in photos
            ]
            return image_urls
    except Exception as e:
        logMsg(f"Error searching Flickr for '{searchTerm}': {str(e)}")

    return []

import requests
import os
from datetime import datetime
import json
import time


def search_wikipedia(keyword):
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

def get_images_from_page(title):
    """
    Get the first 10 image URLs from a given Wikipedia page title.
    """
    API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'images',
        'format': 'json'
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        pages = response.json().get('query', {}).get('pages', {})

        image_titles = []
        for page_id, page in pages.items():
            if 'images' in page:
                image_titles = [img['title'] for img in page['images'][:10]]
                break

        image_urls = []
        for title in image_titles:
            image_url = get_image_url(title)
            if image_url:
                image_urls.append(image_url)

        return image_urls
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
    """
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


def main():
    # Read JSON data from the file
    json_filepath = '../data/subjects/bkds_places_subj.json'
    with open(json_filepath, 'r') as file:
        json_data = json.load(file)

    output_data = []

    # Process each keyword
    for item in json_data:
        time.sleep(2)
        keyword = item['keyword']
        search_results = search_wikipedia(keyword)
        print(f'keyword: {keyword}')
        for result in search_results:
            time.sleep(1)
            print(f'result: {result}')
            images = get_images_from_page(result['title'])
            print(f'images: {images}')

            output_data.append({
                "Search Term": keyword,
                "Page URL": result['wiki_url'],
                "Images": images
            })

    # Save the output data to a JSON file with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filepath = f'../data/output/bkds_places_subj_{timestamp}.json'
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, 'w') as file:
        json.dump(output_data, file, indent=4)

    return output_filepath

# Running the main function and getting the path of the output file
main()

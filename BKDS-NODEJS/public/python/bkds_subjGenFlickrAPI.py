import requests

def getFlickrData(keyword, num_images, api_key):
    """
    Searches Flickr for images related to a given keyword.

    :param keyword: The search term for the image search.
    :param num_images: The number of images to retrieve.
    :param api_key: The API key for accessing Flickr services.
    :return: A list of URLs of the found images.
    """
    print(f"Searching Flickr for: {keyword}")
    base_url = "https://www.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
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
            image_urls = [
                f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}.jpg" 
                for photo in photos
            ]
            return image_urls
    except Exception as e:
        print(f"Error searching Flickr for '{keyword}': {str(e)}")

    return []

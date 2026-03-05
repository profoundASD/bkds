import re
import json

#filename = '/home/aimless76/Downloads/yt_html/C-130 Hercules - YouTube.html'
filename = '/home/aimless76/Downloads/List of unmanned aerial vehicles of China - YouTube.html'

def extract_video_data(html_content):
    # Regular expression to find all occurrences of the videoId and thumbnail pattern
    pattern = r'"videoId":"(\w+)","thumbnail":\{"thumbnails":\[\{"url":"([^"]+)"'
    
    # Find all matches in the HTML content
    matches = re.findall(pattern, html_content)
    
    # Using a dictionary to store unique videoId-thumbnail pairs (dictionaries maintain insertion order since Python 3.7)
    unique_data = {}
    
    # Loop through matches and add them to the dictionary to ensure uniqueness
    for video_id, thumbnail_url in matches:
        if video_id not in unique_data:
            unique_data[video_id] = thumbnail_url
    
    # Convert dictionary to list of JSON objects for easier manipulation or display, adding a sequence ID and video_url
    video_list = [{
        "result_id": idx + 1,
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "video_thumb": thumbnail_url,
    } for idx, (video_id, thumbnail_url) in enumerate(unique_data.items())]
    
    return video_list

def main():
    # Reading the HTML content from a file
    with open(filename, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Extract video data from HTML content
    video_data = extract_video_data(html_content)
    
    # Print each unique videoId-thumbnail pair with an ID in JSON format
    for data in video_data:
        print(json.dumps(data, indent=4))

if __name__ == "__main__":
    main()

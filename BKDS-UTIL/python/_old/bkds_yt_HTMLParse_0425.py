import re
import json
import os
import datetime
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
from better_profanity import profanity
from bkdsUtilities import log_msg

#####################################################################
# Main Setup / Variables

# Process HTML files to extract YouTube video data and store results in JSON format in the specified directory.
input_dir = '/home/aimless76/Documents/Sync/vmShare/vmMate00/vmMate00_ytScrape'
output_dir = os.getenv('BKDS_UTIL_DATA')
batch_id = 'BKDS_UTIL_DATA'
program_name = os.path.basename(__file__)

if output_dir:
    output_dir = os.path.join(output_dir, 'output', 'yt_scrape')
    print("Output directory set to:", output_dir)
else:
    print("Environment variable 'BKDS_NODEJS_SUBJGEN' not found.")
    output_dir = './'  # Default to current directory if environment variable is not set

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def remove_urls(text):
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)

def clean_profanity(text):
    return profanity.censor(text)

def parse_ids_from_filename(filename):
    parts = filename.split('_')
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return None, None, None

def extract_video_data(html_content, filename, insight_id, search_id, subject_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    video_data = []
    timestamp = datetime.datetime.now().isoformat()

    video_elements = soup.find_all('ytd-video-renderer', class_="style-scope ytd-item-section-renderer")
    for idx, element in enumerate(video_elements):
        video_url_tag = element.find('a', id="thumbnail")
        video_url = video_url_tag['href'] if video_url_tag else ''
        
        # Skip processing if URL contains '/shorts/'
        if '/shorts/' in video_url:
            logMsg(f'Skipping video with URL containing /shorts/: {video_url}')
            continue

        try:
            video_id = video_url.split('v=')[1].split('&')[0] if video_url else ''
        except IndexError:
            logMsg(f'Skipping video due to parsing error in URL: {video_url}')
            continue

        video_thumb = f"https://i.ytimg.com/vi/{video_id}/hq720.jpg"

        title_wrapper = element.find('div', id="title-wrapper")
        video_title_tag = title_wrapper.find('a', id="video-title") if title_wrapper else None
        video_title = video_title_tag['title'] if video_title_tag else ''

        video_data.append({
            "file_name": filename,
            "processed_time": timestamp,
            "result_id": idx + 1,
            "insight_id": insight_id,
            "search_id": search_id,
            "subject_id": subject_id,
            "video_id": video_id,
            "video_url": video_url,
            "video_thumb": video_thumb,
            "video_title": video_title,
            "video_description": ''
        })

    return video_data


def extract_video_desc(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    video_data = []

    # Finding all thumbnails, each representing a video
    thumbnails = soup.find_all('ytd-thumbnail', class_="style-scope ytd-video-renderer")
    for idx, thumbnail in enumerate(thumbnails):
        # Finding description in the larger context, need to adjust scope to each video individually
        metadata_container = thumbnail.parent if thumbnail.parent else soup
        description_tag = metadata_container.find('yt-formatted-string', class_='metadata-snippet-text')
        video_description = ' '.join(description_tag.stripped_strings) if description_tag else ''

        video_data.append({
            "result_id": idx + 1,
            "video_description": remove_urls(clean_profanity(video_description))
        })

    return video_data

def combine_video_data(video_data, video_desc_data):
    combined_data = []

    for video, desc in zip(video_data, video_desc_data):
        if video['result_id'] == desc['result_id']:  # Ensure sequence alignment
            combined_entry = video.copy()
            combined_entry.update({
                "video_description": desc["video_description"]  # Only update description
            })
            combined_data.append(combined_entry)

    return combined_data

def process_files(directory):
    all_video_data = []
    for filename in os.listdir(directory):
        logMsg(f'processing filename: {filename}')
        if filename.endswith(".html"):
            full_path = os.path.join(directory, filename)
            insight_id, search_id, subject_id = parse_ids_from_filename(filename)
            with open(full_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            video_data = extract_video_data(html_content, filename, insight_id, search_id, subject_id)
            video_desc_data = extract_video_desc(html_content)
            combined_data = combine_video_data(video_data, video_desc_data)
            all_video_data.extend(combined_data)

    output_file_name = f'all_videos_data_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    output_file = os.path.join(output_dir, output_file_name)
    with open(output_file, 'w', encoding='utf-8') as file:
        logMsg(f'writing output to: {output_file}')
        json.dump(all_video_data, file, indent=4)

# Main
if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    process_files(input_dir)
import re
import json
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
from better_profanity import profanity
from bkds_Utilities import log_msg
import argparse

#####################################################################
# Main Setup / Variables

# Process HTML files to extract YouTube video data and store results in JSON format in the specified directory.

parser = argparse.ArgumentParser(description="Load JSON data into PostgreSQL database.")
parser.add_argument("batch_id", help="batch_id required")
parser.add_argument("proc_type", help="proc_type required", default='yt_alt')
parser.add_argument("data_type", help="data type required", default='html')

args = parser.parse_args()
batch_id = args.batch_id + 'YT_HTML_PARSE'
proc_type = args.proc_type
data_type = args.data_type

#input_dir = '/home/aimless76/Documents/Sync/vmShare/vmMate00/vmMate00_ytScrape'
source_file='search_terms_20240509164038.json'
output_dir = os.getenv('BKDS_UTIL_DATA')
input_dir = output_dir

program_name = os.path.basename(__file__)

if output_dir:
    output_dir = os.path.join(output_dir, proc_type, 'output/json')
    print("Output directory set to:", output_dir)
else:
    print("Environment variable 'BKDS_UTIL_DATA' not found.")
    output_dir = './'  # Default to current directory if environment variable is not set


if input_dir:
    source_file = os.path.join(input_dir, proc_type, 'input', source_file)
    input_dir = os.path.join(input_dir, proc_type, data_type)
    print("Input directory set to:", input_dir)
    print(f"using source file: {source_file}")
else:
    print("Environment variable 'BKDS_UTIL_YT_SCRAPE' not found.")
    source_file = './'  # Default to current directory if environment variable is not set

########################################################################
#  Main logic and functions
def logMsg(msg):
    # Assuming log_msg is defined elsewhere to handle the logging
    log_msg(program_name, batch_id, msg)
    print(msg)

def remove_urls(text):
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)

def clean_profanity(text):
    # Assuming profanity.censor is defined elsewhere
    return profanity.censor(text)

def parse_ids_from_filename(filename):
    parts = filename.split('_')
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return None, None, None

def extract_video_data(html_content, filename, insight_id, search_id, subject_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    video_data = []
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    video_elements = soup.find_all('ytd-video-renderer', class_="style-scope ytd-item-section-renderer")
    for idx, element in enumerate(video_elements):
        video_url_tag = element.find('a', id="thumbnail")
        video_url = video_url_tag['href'] if video_url_tag else ''
        
        if '/shorts/' in video_url:
            logMsg(f'Skipping video with URL containing /shorts/: {video_url}')
            continue

        try:
            video_id = video_url.split('v=')[1].split('&')[0] if video_url else ''
        except IndexError:
            logMsg(f'Skipping video due to parsing error in URL: {video_url}')
            continue

        video_thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        title_wrapper = element.find('div', id="title-wrapper")
        video_title_tag = title_wrapper.find('a', id="video-title") if title_wrapper else None
        video_title = video_title_tag['title'] if video_title_tag else ''

        video_data.append({
            "title": video_title,
            "thumbnail": video_thumb,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "timestamp": timestamp,
            "result_id": idx + 1
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


def load_source_data(source_file):
    with open(source_file, 'r', encoding='utf-8') as file:
        source_data = json.load(file)
    # Create a dictionary for quick lookup, storing both category and search term
    lookup_dict = {(item['subject_id'], item['insight_id'], item['search_id']): (item['data_category'], item['search_term']) for item in source_data}
    return lookup_dict

def get_data_attributes(subject_id, insight_id, search_id, lookup_dict):
    # Using the tuple of identifiers to get the category and search term
    print(f'subject_id: {subject_id} insight_id: {insight_id} search_id: {search_id}')
    return lookup_dict.get((subject_id, insight_id, search_id), ("unknown", "Unknown Search Term"))  # Defaults if not found

def process_files(directory, output_dir, source_file):
    # Load source data once
    source_lookup = load_source_data(source_file)
    #print(f'source_lookup: {source_lookup}')

    
    all_video_data = []
    for filename in os.listdir(directory):
        logMsg(f'processing filename: {filename}')
        if filename.endswith(".html"):
            full_path = os.path.join(directory, filename)
            insight_id, subject_id, search_id  = parse_ids_from_filename(filename)
            with open(full_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            video_data = extract_video_data(html_content, filename, insight_id, search_id, subject_id)
            video_desc = extract_video_desc(html_content)
            combined_video_data = combine_video_data(video_data, video_desc)
            utc_time = datetime.now().strftime("%Y%m%d%H%M%S")
            
            category, search_term = get_data_attributes(subject_id, insight_id, search_id, source_lookup)

            all_video_data.append({
                    "searchID": search_id,
                    "subjectID": subject_id,
                    "resultID": filename,
                    "insightID": insight_id,
                    "category": category,
                    "dataSource": "youtube",
                    "searchTerm": search_term,
                    "api_results": combined_video_data,
                    "utcTime": utc_time
                })

    output_file_name = f'{proc_type}_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    output_file = os.path.join(output_dir, output_file_name)
    with open(output_file, 'w', encoding='utf-8') as file:
        logMsg(f'writing output to: {output_file}')
        json.dump(all_video_data, file, indent=4)


# Main
if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    process_files(input_dir, output_dir, source_file)
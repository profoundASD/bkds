import re
import json
import os
from datetime import datetime
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

def extract_video_data(html_content):
    pattern = r'"videoId":"(\w+)",.*?"thumbnail":\{"thumbnails":\[\{"url":"([^"]+)".*?"descriptionSnippet":\{"runs":\[\{"text":"([^"]+)"'
    matches = re.findall(pattern, html_content)
    unique_data = {}
    for video_id, thumbnail_url, description in matches:
        if video_id not in unique_data:
            unique_data[video_id] = {
                "thumbnail_url": thumbnail_url,
                "description": description
            }
    return unique_data

def parse_ids_from_filename(filename):
    parts = filename.split('_')
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return None, None, None
# Function to get a formatted timestamp
def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def process_files(directory):
    all_video_data = []
    for filename in os.listdir(directory):
        logMsg(f'processing filename: {filename}')
        if filename.endswith(".html"):
            full_path = os.path.join(directory, filename)
            insight_id, search_id, subject_id = parse_ids_from_filename(filename)
            with open(full_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            video_data = extract_video_data(html_content)
            timestamp = datetime.now().isoformat()  # Get current timestamp in ISO format
            video_list = [{
                "file_name": filename,
                "processed_time": timestamp,
                "result_id": idx + 1,
                "insight_id": insight_id,
                "search_id": search_id,
                "subject_id": subject_id,
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "video_thumb": data["thumbnail_url"],
                "description": clean_profanity(remove_urls(data["description"].replace('\r', '').replace('\n', '').replace('\\n', '')))
            } for idx, (video_id, data) in enumerate(video_data.items())]
            all_video_data.extend(video_list)
    
    # Write all data to a JSON file with a timestamp in the filename
    output_file_name = f'all_videos_data_{get_timestamp()}.json'
    output_file = os.path.join(output_dir, output_file_name)
    with open(output_file, 'w', encoding='utf-8') as file:
        logMsg(f'writing output to: {output_file}')
        json.dump(all_video_data, file, indent=4)

def main():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    process_files(input_dir)

if __name__ == "__main__":
    main()

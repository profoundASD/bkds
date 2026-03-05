import os
import re
import json
import time
import ujson
import zipfile
import argparse
from datetime import datetime
from bkds_Utilities import log_msg, fetch_data, get_sqlTemplate, split_text_into_spans
program_name = os.path.basename(__file__)

# Main Setup / Variables
out_dir = os.getenv('BKDS_NODEJS_DATA')
util_dir = os.getenv('BKDS_NODEJS_DATA')
production_base_path="/data/images/full_size/"
data_type = 'config'
archive_folder = 'archive'
archive_folder_path = os.path.join(util_dir, data_type, archive_folder)
input_type = 'json'
index_file_name = 'bkds_category_index' + '.' + input_type
index_base_path = os.path.join(util_dir, data_type)
index_file_path = os.path.join(index_base_path, index_file_name)
target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process insights and related media content into JSON files based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    parser.add_argument("--gen_type", choices=['all', 'details', 'sample'], default='all', help="Type of output file to generate: 'details' for detailed data, 'sample' for random samples, 'all' for both.")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
gen_type = args.gen_type
insight_query_key = 'bkds_contentGen_web_feed_master'
output_type = 'json'
output_prefix = 'bkds_' 
subjType = 'contentPostGen'
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

def logMsg(msg):
    """ Log a message to the console and using a logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)

def safely_parse_json(json_data):
    if isinstance(json_data, str):
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            logMsg("Failed to decode JSON data.")
            return []
    return json_data

def transform_data(insights):
    logMsg(f"Starting transform_data @ {datetime.now()}")
    transformed_data = {}
    
    for record in insights:
        data_category = record.get('data_category', '')
        data_subject = record.get('data_subject', '')
        content = record.get('subject_content', '')

        # Process the content using the new function
        processed_content = split_text_into_spans(content)

        insight_details = {
            "url_id": record.get('url_id', ''),
            "cluster_id": record.get('cluster_id', ''),
            "subject_id": record.get('subject_id', ''),
            "subject_title": record.get('subject_title', ''),
            "data_category": data_category,
            "data_category_id": record.get('data_category_id', ''),
            "data_subject": data_subject,
            "data_subject_id": record.get('data_subject_id', 'NO ID'),
            "content_name": record.get('content_name', '')
        }

        text_block = {
            "source": record.get('page_url', ''),
            "content": processed_content,  # Use the processed content here
            "description": "Overview of " + record.get('subject_title', '')
        }

        # Parse image data and organize them with labels
        featured_images = safely_parse_json(record.get('featured_images', '[]'))
        gallery_images = safely_parse_json(record.get('images', '[]'))
        
        # Process both featured and gallery images
        media_images = process_images(gallery_images, featured_images, data_subject, data_category)
        media_videos = process_videos(record.get('videos', '[]'))

        # Find the default image URL
        default_image_url = process_url((record.get('default_img', '[]')))
        
        media = {
            "videos": media_videos,
            "images": media_images,
            "default_img": default_image_url
        }
        related_topics = safely_parse_json(record.get('related_topics', '[]'))

        if data_category not in transformed_data:
            transformed_data[data_category] = {}
        transformed_data[data_category][record.get('url_id', '')] = {
            "insight_details": insight_details,
            "text_block": text_block,
            "media": media,
            "related_topics": related_topics
        }
    
    logMsg(f"Completed transform_data @ {datetime.now()}")
    return transformed_data


def save_to_json(transformed_data, out_dir):
    logMsg("Starting save_to_json")

    for category, items in transformed_data.items():
        category_output_dir = os.path.join(out_dir, content_root, category)
        os.makedirs(category_output_dir, exist_ok=True)
        archive_dir = os.path.join(category_output_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        #logMsg(f"Created directory {category_output_dir}")

        for url_id, item in items.items():
            content_name = item['insight_details'].get('content_name', 'default_content_name')
            cluster_id = item['insight_details'].get('cluster_id', 'default_cluster')

            # Determine the output path for each URL_ID based on content_name and cluster_id
            if content_name == 'main_feed':
                subject_output_path = os.path.join(category_output_dir, f"bkds_main_feed.json")
            else:
                content_dir = os.path.join(category_output_dir, cluster_id, url_id)
                os.makedirs(content_dir, exist_ok=True)
                subject_output_path = os.path.join(content_dir, f"{url_id}_{content_name}.json")

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            raw_output_path = os.path.join(content_dir, f"{url_id}_{content_name}_raw_{timestamp}.json")
            archive_path = os.path.join(archive_dir, f"{url_id}_{content_name}_{timestamp}.zip")

            try:
                # Write minimized JSON data directly
                with open(raw_output_path, 'w') as f:
                    ujson.dump([item], f)  # Save directly as minimized JSON

                #logMsg(f"Raw JSON file for {url_id} in content {content_name} saved successfully at {raw_output_path}")

                # Read the raw JSON data using ujson
                with open(raw_output_path, 'r') as f:
                    raw_json_data = ujson.load(f)

                # Minify the JSON data without extra spaces or line breaks
                minimized_json = ujson.dumps(raw_json_data)

                # Compare with existing file content if it exists
                if os.path.exists(subject_output_path):
                    with open(subject_output_path, 'r') as f:
                        existing_data = ujson.load(f)

                    # Serialize both datasets for comparison
                    existing_data_serialized = ujson.dumps(existing_data)
                    new_data_serialized = minimized_json

                    # Compare the existing data with the new data
                    if existing_data_serialized == new_data_serialized:
                        #logMsg(f"No changes detected for {subject_output_path}. Skipping write.")
                        os.remove(raw_output_path)  # Clean up raw file
                        continue

                    timestamped_output_path = f"{subject_output_path}_{timestamp}"
                    os.rename(subject_output_path, timestamped_output_path)
                    #logMsg(f"Renamed existing JSON file to {timestamped_output_path}")

                    with zipfile.ZipFile(archive_path, 'w') as archive:
                        archive.write(raw_output_path, os.path.basename(raw_output_path))
                        archive.write(timestamped_output_path, os.path.basename(timestamped_output_path))
                        #logMsg(f"Archive created successfully at {archive_path}")

                    # Delete the previous batch file after archiving
                    os.remove(timestamped_output_path)
                    #logMsg(f"Deleted previous batch file after archiving")
                else:
                    with zipfile.ZipFile(archive_path, 'w') as archive:
                        archive.write(raw_output_path, os.path.basename(raw_output_path))
                        #logMsg(f"Archive created successfully at {archive_path}")

                # Write the minified JSON data
                with open(subject_output_path, 'w') as f:
                    f.write(minimized_json)

                #logMsg(f"JSON file for {url_id} in content {content_name} saved successfully at {subject_output_path}")

                # Delete the raw file after archiving
                os.remove(raw_output_path)
                #logMsg(f"Deleted raw batch file after archiving")

            except Exception as e:
                logMsg(f"Failed to save JSON file for {url_id} at {subject_output_path}: {e}")

def process_url(url):
    # Mapping of patterns to folders
    pattern_to_folder = {
        'yt': 'youtube',
        'youtube': 'youtube',
        'flickr': 'flickr',
        'wiki': 'wiki'
    }
    
    # Regex to check if the URL is an actual URL
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    # If the URL is not a valid URL, assume it's a local path
    if not re.match(url_regex, url):
        file_name = os.path.basename(url)
        for pattern, folder in pattern_to_folder.items():
            if pattern in url:
                return os.path.join(production_base_path, folder, file_name)
        # Default case if no pattern is matched
        return os.path.join(production_base_path, file_name)
    return url

def process_videos(video_list):
    processed_videos = {}  # Use a different name for the dictionary to avoid confusion and conflicts
    
    # First pass: Process all videos
    for video in video_list:
        vid_id = video['vid_url_id']
        if vid_id not in processed_videos:
            processed_videos[vid_id] = {
                'vid_url_id': vid_id,
                'vid_url': process_url(video['vid_url']),  # Store processed video URL
                'vid_title': video['vid_title'],  # Store video title
                'vid_thumb_url': process_url(video['vid_thumb_url']),  # Store processed thumbnail URL
                'label': 'gallery'  # Assign label
            }
    
    # Convert the dictionary back to a list for output
    return list(processed_videos.values())

def process_images(gallery_images, featured_images, data_subject, data_category):
    # Initialize a list to store images
    images = []

    # First pass: Add all gallery images with label 'gallery'
    for img in gallery_images:
        images.append({
            'img_url_id': img['img_url_id'],
            'img_url': process_url(img['img_url']),  # Store processed image URL
            'img_title': img['img_title'],  # Store image title
            'img_desc1': img['img_desc1'],  # Store image title
            'img_desc2': img['img_desc2'],  # Store image title
            'data_category': data_category,  # Store image title
            'data_subject': data_subject,  # Store image title
            'label': 'gallery'
        })

    # Second pass: Add/Update featured images, which take precedence over gallery images
    for img in featured_images:
        found = False
        for i in range(len(images)):
            if images[i]['img_url_id'] == img['img_url_id']:
                # Update existing entry if found
                images[i] = {
                    'img_url_id': img['img_url_id'],
                    'img_url': process_url(img['img_url']),  # Update the URL
                    'img_title': img['img_title'],  # Update the title
                    'img_desc1': img['img_desc1'],  #img description data
                    'img_desc2': img['img_desc2'],  
             #       'img_desc3': img['img_desc3'],  
                    'img_src':   img['img_src'],  
                    'data_category': data_category,  # Store image title
                    'data_subject': data_subject,  # Store image title
                    'label': 'featured'
                }
                found = True
                break
        if not found:
            # Add new entry if not found
            images.append({
                'img_url_id': img['img_url_id'],
                'img_url': process_url(img['img_url']),  # Store processed image URL
                'img_title': img['img_title'],  # Store image title
                'img_desc1': img['img_desc1'],  #img description data
                'img_desc2': img['img_desc2'],  
      #          'img_desc3': img['img_desc3'],  
                'img_src':   img['img_src'],                  
                'data_category': data_category,  # Store image title
                'data_subject': data_subject,  # Store image title
                'label': 'featured'
            })

    return images


def main():
    """ Main execution function. """
    logMsg(f"Starting main @ {datetime.now()}")

    insights = fetch_data(get_sqlTemplate(insight_query_key))
    category_data = transform_data(insights)
    save_to_json(category_data, out_dir)
    
    logMsg("Script execution completed.")

if __name__ == "__main__":
    main()

import os
import re
import ujson
import time
import random
import argparse
import zipfile
from datetime import datetime
from collections import defaultdict
from bkdsUtilities import log_msg, fetch_data, get_sqlTemplate

# Main Setup / Variables
out_dir = os.getenv('BKDS_NODEJS_DATA')
production_base_path = os.path.join(out_dir, "images/full_size/")
target_base_path = '/data/images/full_size/'
program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process images into a JSON file based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
insight_query_key = 'bkds_contentGen_web_feed_master'
output_file = os.path.join(out_dir, "images", f"master_image_index.json")
archive_dir = os.path.join(out_dir, "archive")

def logMsg(msg):
    """ Log a message to the console and using a logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)

def safely_parse_json(json_data):
    if isinstance(json_data, str):
        try:
            return ujson.loads(json_data)
        except ujson.JSONDecodeError:
            logMsg("Failed to decode JSON data.")
            return []
    return json_data

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
        return os.path.join(production_base_path, file_name)
    return url

def process_images(gallery_images, featured_images, data_category, data_subject, img_dict):
    written_count = 0
    skipped_count = 0
    substituted_count = 0

    def add_or_update_image(img, label):
        nonlocal written_count, skipped_count, substituted_count
        img_url = process_url(img['img_url'])
        img_path = img_url if img_url.startswith('http') else os.path.join(production_base_path, img_url)

        if not os.path.exists(img_path):
            skipped_count += 1
            return

        pil_img_path = img_path.replace('.jpg', '_PIL_200.jpg')
        if os.path.exists(pil_img_path):
            img_url = pil_img_path
            substituted_count += 1

        img_url = img_url.replace(production_base_path, target_base_path)
        
        if img['img_url_id'] in img_dict:
            img_dict[img['img_url_id']]['data_category'].add(data_category)
            img_dict[img['img_url_id']]['data_subject'].add(data_subject)
            img_dict[img['img_url_id']]['label'] = label  # Update label if already exists
        else:
            img_dict[img['img_url_id']] = {
                'img_url_id': img['img_url_id'],
                'img_url': img_url,
                'img_title': img['img_title'],
                'img_desc1': img.get('img_desc1', ''),
                'img_desc2': img.get('img_desc2', ''),
                'img_desc3': img.get('img_desc3', ''),
                'img_src': img.get('img_src', ''),
                'label': label,
                'data_category': {data_category},
                'data_subject': {data_subject}
            }
        written_count += 1

    # First pass: Add all gallery images with label 'gallery'
    for img in gallery_images:
        add_or_update_image(img, 'gallery')

    # Second pass: Add/Update featured images, which take precedence over gallery images
    for img in featured_images:
        add_or_update_image(img, 'featured')

    logMsg(f"Images processed: Written={written_count}, Skipped={skipped_count}, Substituted Thumbnails={substituted_count}")



def transform_data(insights):
    logMsg(f"Starting transform_data @ {datetime.now()}")
    img_dict = {}

    for record in insights:
        data_category = record.get('data_category', '')
        data_subject = record.get('data_subject', '')
        gallery_images = safely_parse_json(record.get('images', '[]'))
        featured_images = safely_parse_json(record.get('featured_images', '[]'))
        process_images(gallery_images, featured_images, data_category, data_subject, img_dict)

    # Convert sets to lists
    images = [
        {
            **img_data,
            'data_category': list(img_data['data_category']),
            'data_subject': list(img_data['data_subject'])
        }
        for img_data in img_dict.values()
    ]

    # Shuffle the images randomly
    random.shuffle(images)

    logMsg(f"Completed transform_data @ {datetime.now()}")
    return images

def save_to_json(data, output_file, archive_dir):
    logMsg("Starting save_to_json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    new_data_serialized = ujson.dumps(data)

    # If the file exists, check for changes
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_data = ujson.load(f)
        existing_data_serialized = ujson.dumps(existing_data)
        
        # If there is no change, skip saving
        if existing_data_serialized == new_data_serialized:
            logMsg("No changes detected. Skipping file save.")
            return
        
        # If there are changes, archive the existing file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_file = os.path.join(archive_dir, f"image_index_{timestamp}.zip")
        with zipfile.ZipFile(archive_file, 'w') as archive:
            archive.write(output_file, os.path.basename(output_file))
        logMsg(f"Archived existing file to {archive_file}")

    # Save the new data to the output file
    with open(output_file, 'w') as outfile:
        outfile.write(new_data_serialized)
    logMsg(f"JSON file saved successfully at {output_file}")

def main():
    """ Main execution function. """
    logMsg(f"Starting main @ {datetime.now()}")
    insights = fetch_data(get_sqlTemplate(insight_query_key))
    images_data = transform_data(insights)
    save_to_json(images_data, output_file, archive_dir)
    logMsg("Script execution completed.")

if __name__ == "__main__":
    main()

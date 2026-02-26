import os
import json
import shutil
import argparse
from datetime import datetime
import time
import random
from bkdsUtilities import log_msg, fetch_data, subjGenOutputHandler, get_sqlTemplate

"""
This script processes and combines data from multiple database queries into JSON files.
Each JSON file contains insights along with associated videos, images, and text content, aggregated by data_category.
The data is grouped by `data_category` and saved into files based on the structured data retrieved from a PostgreSQL database.
The program uses batch processing for handling large datasets and logs essential information for debugging and monitoring.

Author: [Your Name]
Date: [Last Updated Date]
Usage: Run the script with a batch ID to process specific subjects.
Example: python [script_name].py <batch_id>
"""
#####################################################################
# Main Setup / Variables
nodejs_dir=os.getenv('BKDS_UTIL_DATA')
util_dir=os.getenv('BKDS_UTIL_DATA')
data_type='config'
archive_folder='archive'
archive_folder_path = os.path.join(util_dir,  data_type, archive_folder)
input_type='json'
index_file_name='bkds_category_index'+'.'+input_type
print(f'index_file_name {index_file_name}')
index_base_path = os.path.join(util_dir, data_type)
index_file_path = os.path.join(index_base_path,index_file_name)
print(f'util_dir {util_dir}')
content_path=os.path.join(util_dir, 'subjGen/contentPostGen/output/json')
print(f'content_path: {content_path} with util_dir: {util_dir}')


########################################################################
#  Main logic and functions
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process insights and related media content into JSON files based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    parser.add_argument("--gen_type", choices=['all', 'details', 'sample'], default='all',
                        help="Type of output file to generate: 'details' for detailed data, 'sample' for random samples, 'all' for both.")
    return parser.parse_args()

def initialize():
    """ Initialize configuration and global variables. """
    global args, batch_id, program_name, insight_query_key, videos_query_key, images_query_key, texts_query_key
    global output_type, output_prefix, subjType, timestamp, gen_type
    args = parse_arguments()
    batch_id = args.batch_id
    gen_type = args.gen_type
    program_name = os.path.basename(__file__)
    insight_query_key = 'bkds_contentGen_insight_query_key'
    videos_query_key = 'bkds_contentGen_videos_query_key'
    images_query_key = 'bkds_contentGen_img_query_key'
    texts_query_key = 'bkds_contentGen_text_query_key'
    output_type = 'json'
    output_prefix = 'bkds_'
    subjType = 'contentPostGen'
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

def logMsg(msg):
    """ Log a message to the console and using a logging system. """
    log_msg(program_name, batch_id, msg)
    print(msg)

def initialize_media(category_data, insights, videos, images, texts):
    """ Initialize media content into category data based on insight_id mappings. """
    # Mapping from insight_id to its category for quick lookup
    insight_map = {insight['insight_id']: insight.get('data_category', 'Uncategorized') for insight in insights}

    # Setup media initialization with minimal unique fields
    for media_list, media_type, unique_fields in [
        (videos, 'videos', ['video_url', 'video_title', 'thumb_url', 'description', 'data_source']),
        (images, 'images', ['image_url', 'description', 'data_source']),
        (texts, 'texts', ['page_url', 'subject_content', 'description', 'data_source'])
    ]:
        for media in media_list:
            insight_id = media['insight_id']
            category = insight_map.get(insight_id, 'Uncategorized')
            if insight_id in category_data[category]:
                # Create a simplified dictionary with only unique fields for each media item
                media_details = {field: media[field] for field in unique_fields if field in media}
                category_data[category][insight_id][media_type].append(media_details)

def aggregate_data(insights, videos, images, texts):
    logMsg("Starting data aggregation.")
    category_data = {cat: {} for insight in insights for cat in [insight.get('data_category', 'Uncategorized')]}

    # Populate each category with a structure for insights and their media content
    for insight in insights:
        category = insight.get('data_category', 'Uncategorized')
        insight_id = insight['insight_id']
        if category not in category_data:
            category_data[category] = {}
        if insight_id not in category_data[category]:
            category_data[category][insight_id] = {
                'insight_details': {
                    "insight_id": insight_id,
                    "search_id": insight['search_id'],
                    "subject_id": insight['subject_id'],
                    "subject_title": insight['search_term'],
                    "search_term": insight['subject_title'],
                    "data_category": insight['data_category'],
                    "data_subject": insight['data_subject']
                },
                'videos': [],
                'images': [],
                'texts': []
            }

    initialize_media(category_data, insights, videos, images, texts)
    logMsg("Data aggregation completed.")
    return category_data

def get_insight_details(insight_id, insights):
    """ Extract and return details for a given insight_id from insights list. """
    return next((insight for insight in insights if insight['insight_id'] == insight_id), {})

def save_to_json(output_data, gen_type):
    logMsg(f"Starting JSON file generation for {gen_type}.")
    new_index_data = {}  # This dictionary will track the new index

    if gen_type in ["all", "details"]:
        for category, insights in output_data.items():
            insights_list = [{**{"insight_id": insight_id}, **details} for insight_id, details in insights.items()]
            output_filepath = subjGenOutputHandler(insights_list, subjType, output_prefix, output_type, timestamp, category)
            with open(output_filepath, 'w') as f:
                json.dump(insights_list, f, indent=4)
            logMsg(f"Saved detailed JSON file for category {category}: {output_filepath}")
            new_index_data[category] = output_filepath  # Record the filepath in the index

    if gen_type in ["sample", "all"]:
        all_insights = []
        for category, insights in output_data.items():
            for insight_id, details in insights.items():
                if any(video.get('video_url') for video in details['videos']):
                    all_insights.insert(0, (insight_id, category, details))
                else:
                    all_insights.append((insight_id, category, details))

        sampled_data = random.sample(all_insights, min(50, len(all_insights)))
        sampled_insights_list = [{"insight_id": insight[0], "category": insight[1], **insight[2]} for insight in sampled_data]
        category='main_feed'
        output_filepath = subjGenOutputHandler(sampled_insights_list, subjType, output_prefix, output_type, timestamp, category)
        with open(output_filepath, 'w') as f:
            json.dump(sampled_insights_list, f, indent=4)
        logMsg(f"Saved sample JSON file: {output_filepath}")
        new_index_data[category] = output_filepath  # Record the filepath in the index

    if new_index_data:
        update_index(new_index_data)  # Update the index with new file paths
        print(f'index updated')
        
    logMsg("JSON file generation completed.")

def list_files_in_directory(path):
    """ List all JSON files in the specified directory.
        If a file path is provided, use its parent directory. """
    # Check if the provided path is a file
    if os.path.isfile(path):
        directory = os.path.dirname(path)
        print(f'got directory: {directory}')
    else:
        directory = path
    
    # List all JSON files in the determined directory
    print(f'returning with {input_type}')
 
    return [file for file in os.listdir(directory) if file.endswith(input_type)]


def archive_index():
    # Create an archive folder if it doesn't exist
    if not os.path.exists(archive_folder_path):
        os.makedirs(archive_folder_path)

    # Archive the existing index file with a timestamp
    if os.path.exists(index_file_path):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        archived_file_path = os.path.join(archive_folder_path, f'{index_file_name}_{timestamp}.{input_type}')
        shutil.move(index_file_path, archived_file_path)
        logMsg(f"Archived index file to {archived_file_path}")

def extract_category_from_filename(filename):
    """ Extract the category from the filename where the category is the 2nd to last '_XXX_' string. """
    parts = filename.split('_')
    print(f'parts: {parts}')
    #time.sleep(30)
    # Ensure there are enough parts to avoid index errors
    if len(parts) >= 4:  # Check increased to 4 to ensure there's enough segments
        return parts[-2]  # The 2nd to last part is the category
    else:
        return "Unknown"  # Return a default or error category if the format is not as expected


def update_index(new_index_data):
    """ Update the index file with paths to all JSON files in the base directory. """
    with open(index_file_path, 'w') as f:
        json.dump(new_index_data, f, indent=4)
    logMsg(f"Updated index file with new paths at {index_file_path}.")

    
def main():
    """ Main execution function. """
    logMsg("Script execution started.")
    archive_index()  # Make sure this function or its logic is defined to handle archiving
    insights = fetch_data(get_sqlTemplate(insight_query_key))
    videos = fetch_data(get_sqlTemplate(videos_query_key))
    images = fetch_data(get_sqlTemplate(images_query_key))
    texts = fetch_data(get_sqlTemplate(texts_query_key))
    category_data = aggregate_data(insights, videos, images, texts)
    save_to_json(category_data, gen_type)
    print(f'saved to json')
    logMsg("Script execution completed.")
    
if __name__ == "__main__":
    initialize()
    main()
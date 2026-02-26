import os
import json
import argparse
import datetime
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

def initialize():
    """ Initialize configuration and global variables. """
    global args, batch_id, program_name, insight_query_key, videos_query_key, images_query_key, texts_query_key
    global output_type, output_prefix, subjType, timestamp
    args = parse_arguments()
    batch_id = args.batch_id
    program_name = os.path.basename(__file__)
    insight_query_key = 'bkds_contentGen_insight_query_key'
    videos_query_key = 'bkds_contentGen_videos_query_key'
    images_query_key = 'bkds_contentGen_img_query_key'
    texts_query_key = 'bkds_contentGen_text_query_key'
    output_type = 'json'
    output_prefix = 'bkds_'
    subjType = 'contentPostGen'
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process insights and related media content into JSON files based on batch ID.")
    parser.add_argument("batch_id", help="Unique identifier for the batch processing session.")
    return parser.parse_args()

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
                    "subject_title": insight['subject_title'],
                    "search_term": insight['search_term'],
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

def save_to_json(output_data):
    """ Save aggregated data into JSON files, one per data category. """
    logMsg("Starting JSON file generation.")
    for category, insights in output_data.items():
        # Create a list of insights with their ID as a key within the dictionary
        insights_list = []
        for insight_id, details in insights.items():
            insight_dict = {
                "insight_id": insight_id,  # Use insight_id as a key within the dictionary
                "insight_details": details['insight_details'],
                "videos": details['videos'],
                "images": details['images'],
                "texts": details['texts']
            }
            insights_list.append(insight_dict)
        
        # Prepare filename and file path
        filename = f"{output_prefix}{category}_{timestamp}.{output_type}"
        output_filepath = subjGenOutputHandler(insights_list, subjType, output_prefix, output_type, timestamp, category)
        
        # Write to file
        with open(output_filepath, 'w') as f:
            json.dump(insights_list, f, indent=4)  # Dump the list of insights
        logMsg(f"Saved JSON file for category {category}: {output_filepath}")
    logMsg("JSON file generation completed.")


def main():
    """ Main execution function. """
    logMsg("Script execution started.")
    insights = fetch_data(get_sqlTemplate(insight_query_key))
    videos = fetch_data(get_sqlTemplate(videos_query_key))
    images = fetch_data(get_sqlTemplate(images_query_key))
    texts = fetch_data(get_sqlTemplate(texts_query_key))
    category_data = aggregate_data(insights, videos, images, texts)
    save_to_json(category_data)
    logMsg("Script execution completed.")

if __name__ == "__main__":
    initialize()
    main()
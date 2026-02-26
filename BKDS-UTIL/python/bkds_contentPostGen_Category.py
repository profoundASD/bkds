"""
Category Level Feed Generator Script

This script generates category-level feeds from a database of organized JSON files.
It processes all JSON files, extracts relevant insights, and saves the insights in category-specific batch files.

Modules Used:

os: For directory and file path manipulation
json, ujson: For JSON file handling
datetime: For time and date operations
zipfile: For creating zip archives
Functionality:

Load all JSON files from the specified directory, excluding certain filenames
Process the JSON files to extract insights
Save the insights to category-specific batch files
Archive old batch files to avoid redundancy
Usage:

Set environment variables BKDS_UTIL_DATA and BKDS_NODEJS_DATA to appropriate paths
Ensure required modules are installed: json_minify, ujson
Run the script to generate the category-level feeds
Author: [Your Name]
Date: [Date]

"""

import os
import json
import ujson
import zipfile
import random
from datetime import datetime

def log_msg(message):
    print(message)

##################################
# Setup and global variables

util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')
out_file_name = "bkds_data_category_filter_index.json"
target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

# List of filenames to exclude
exclude_filenames = ['main_feed', '_batch']
postLimit = 2500

# Define a dictionary with categories and shuffle intervals
shuffle_intervals = {
    'rocket': 3
}

##################################
# Main logic and functions

def gather_all_json_files(directory, exclude_folder='main_feed'):
    json_files = []
    for root, dirs, files in os.walk(directory):
        # Exclude the specified folder
        dirs[:] = [d for d in dirs if d != exclude_folder]
        for file in files:
            if file.endswith('.json') and not any(exclude in file for exclude in exclude_filenames):
                json_files.append(os.path.join(root, file))
    return json_files

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        log_msg(f"Skipping invalid JSON file: {file_path}")
        return None


def save_category_batch_file(category, insights):
    target_dir = os.path.join(nodejs_data, content_root, category)
    os.makedirs(target_dir, exist_ok=True)
    archive_dir = os.path.join(target_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    # Add data_src_index to each insight
    for index, insight in enumerate(insights):
        insight['data_src_index'] = index

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    final_output_path = os.path.join(target_dir, f"{category}_batch.json")
    archive_path = os.path.join(archive_dir, f"{category}_batch_{timestamp}.zip")

    current_hour = datetime.now().hour
    shuffle_interval = shuffle_intervals.get(category, 1)  # Default interval is 1 (shuffle every time)

    # Shuffle the insights if applicable
    if current_hour % shuffle_interval == 0:
        random.shuffle(insights)

    # Apply special rules for the category
    insights = apply_special_rules(category, insights)

    try:
        new_data_serialized = ujson.dumps(insights)

        # Compare with existing file content if it exists
        if os.path.exists(final_output_path):
            with open(final_output_path, 'r') as f:
                existing_data_serialized = f.read()

            # If data hasn't changed, skip saving
            if existing_data_serialized == new_data_serialized:
                log_msg(f"No changes detected for {final_output_path}. Skipping write.")
                return

            # Archive the old batch file
            timestamped_output_path = f"{final_output_path}_{timestamp}"
            os.rename(final_output_path, timestamped_output_path)
            log_msg(f"Renamed existing batch file to {timestamped_output_path}")

            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.write(timestamped_output_path, os.path.basename(timestamped_output_path))
                log_msg(f"Archive created successfully at {archive_path}")

            os.remove(timestamped_output_path)
            log_msg(f"Deleted previous batch file after archiving")

        # Write the new minimized JSON data to the final output path
        with open(final_output_path, 'w') as f:
            f.write(new_data_serialized)

        log_msg(f"Category batch file saved successfully at {final_output_path}")

    except Exception as e:
        log_msg(f"Error during saving: {e}")



def apply_special_rules(category, insights):
    log_msg(f"apply_special_rules with {category}")
    """
    Apply special rules to a category's insights. Certain categories may have
    rules to make specific insights "sticky" and always appear at the top.

    Args:
        category (str): The category name.
        insights (list): List of insights for the category.

    Returns:
        list: Insights sorted with special rules applied.
    """
    special_rules = {
        "rockets": lambda insight: insight['insight_details']['cluster_id'] == "launches"
    }
    log_msg(f"apply_special_rules with special_rules {special_rules}")

    if category not in special_rules:
        return insights  # No special rules for this category

    # Get the rule for this category
    rule = special_rules[category]
    log_msg(f"apply_special_rules with special_rules[category] {rule}")

    # Apply the rule: sticky items first, then the rest
    sticky_items = [insight for insight in insights if rule(insight)]
    non_sticky_items = [insight for insight in insights if not rule(insight)]

    # Return sticky items followed by the rest
    return sticky_items + non_sticky_items


def save_index_file(index_data):
    # Sort the index data by type ascending alphabetically
    index_data_sorted = sorted(index_data, key=lambda x: x['type'])

    index_file_path = os.path.join(nodejs_data, content_root, out_file_name)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_dir = os.path.join(nodejs_data, content_root, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, f"index_{timestamp}.zip")

    try:
        # Serialize the index data to minimized JSON
        new_data_serialized = ujson.dumps(index_data_sorted)

        # Compare with existing file content if it exists
        if os.path.exists(index_file_path):
            with open(index_file_path, 'r') as f:
                existing_data_serialized = f.read()

            # Compare the existing data with the new data byte-by-byte
            if existing_data_serialized == new_data_serialized:
                log_msg(f"No changes detected for {index_file_path}. Skipping write.")
                return

            timestamped_output_path = f"{index_file_path}_{timestamp}"
            os.rename(index_file_path, timestamped_output_path)
            log_msg(f"Renamed existing index file to {timestamped_output_path}")

            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.write(timestamped_output_path, os.path.basename(timestamped_output_path))
                log_msg(f"Archive created successfully at {archive_path}")

            # Delete the previous index file after archiving
            os.remove(timestamped_output_path)
            log_msg(f"Deleted previous index file after archiving")

        # Write the new minimized JSON data to the final output path
        with open(index_file_path, 'w') as f:
            f.write(new_data_serialized)

        log_msg(f"Index file saved successfully at {index_file_path}")

    except Exception as e:
        log_msg(f"Error during saving index file: {e}")

def main():
    log_msg("Gathering all JSON files from directory...")
    json_files = gather_all_json_files(os.path.join(nodejs_data, content_root))

    all_insights = {}
    index_data_set = set()

    log_msg("Reading and categorizing JSON files...")
    for file_path in json_files:
        data = read_json_file(file_path)
        if data is None:
            continue

        # Determine if the file should be excluded from index_data
        exclude_from_index_data = "launch_update" in file_path

        if isinstance(data, list):
            for record in data:
                insight_details = record.get('insight_details', {})
                category = insight_details.get('data_category', 'uncategorized')
                category_id = insight_details.get('data_category_id', 'uncategorized_id')
                subject = insight_details.get('data_subject', 'uncategorized_subject')
                subject_id = insight_details.get('data_subject_id', 'uncategorized_subject_id')

                # Skip uncategorized entries
                if category == 'uncategorized' or subject == 'uncategorized_subject':
                    continue

                # If the file should not be excluded from index_data, add to index_data_set
                if not exclude_from_index_data:
                    index_data_set.add(("category", category, category_id))
                    index_data_set.add(("subject", subject, subject_id))

                # Extract default image
                default_image = record.get('media', {}).get('default_img') or record.get('default_img', 'default image Missing')

                # Ensure text_block and its fields exist
                text_block_content = record.get('text_block', {}).get('content', 'No data')[:postLimit]
                text_block_description = record.get('text_block', {}).get('description', 'No description')

                trimmed_record = {
                    "insight_details": {
                        "url_id": insight_details.get('url_id', 'Missing'),
                        "cluster_id": insight_details.get('cluster_id', 'Missing'),
                        "subject_id": insight_details.get('subject_id', 'Missing'),
                        "subject_title": insight_details.get('subject_title', 'Missing'),
                        "data_category": insight_details.get('data_category', 'Missing'),
                        "data_category_id": insight_details.get('data_category_id', 'Missing'),
                        "data_subject": insight_details.get('data_subject', 'Missing'),
                        "data_subject_id": insight_details.get('data_subject_id', 'Missing'),
                        "content_name": insight_details.get('content_name', 'Missing')
                    },
                    "default_img": default_image,
                    "text_block": {
                        "content": text_block_content,
                        "description": text_block_description
                    }
                }

                if category not in all_insights:
                    all_insights[category] = []
                all_insights[category].append(trimmed_record)

    # Create a list of unique index entries and sort them by type
    index_data = [{"type": t, "filter_name": name, "filter_id": id} for (t, name, id) in sorted(index_data_set, key=lambda x: x[0])]

    log_msg("Saving category-specific batch files...")
    for category, insights in all_insights.items():
        save_category_batch_file(category, insights)

    log_msg("Saving index file...")
    save_index_file(index_data)

    log_msg("Batch file generation completed.")

if __name__ == "__main__":
    main()

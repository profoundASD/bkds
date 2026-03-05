import os
import json
from json_minify import json_minify  # Ensure you have this package installed via pip
import random

# Set environment variables or replace with actual paths
util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

target_root = "./public/data"
content_root = 'content_feeds'
content_dir = os.path.join(target_root, content_root)

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def log_msg(message):
    print(message)

def gather_all_json_files(directory, exclude_folder='main_feed'):
    json_files = []
    for root, dirs, files in os.walk(directory):
        # Exclude the specified folder
        dirs[:] = [d for d in dirs if d != exclude_folder]
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_category_batch_file(category, insights):
    target_dir = os.path.join(nodejs_data, content_root, category)
    os.makedirs(target_dir, exist_ok=True)
    output_path = os.path.join(target_dir, f"{category}_batch.json")
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=4)
    log_msg(f"Category batch file saved successfully at {output_path}")

def main():

    log_msg("Gathering all JSON files from directory...")
    json_files = gather_all_json_files(os.path.join(nodejs_data, content_root))

    all_insights = {}
    
    log_msg("Reading and categorizing JSON files...")
    for file_path in json_files:
        data = read_json_file(file_path)
        if isinstance(data, list):
            for record in data:
                category = record['insight_details'].get('data_category', 'uncategorized')
                if category not in all_insights:
                    all_insights[category] = []
                all_insights[category].append(record)
    
    log_msg("Saving category-specific batch files...")
    for category, insights in all_insights.items():
        save_category_batch_file(category, insights)
    
    log_msg("Batch file generation completed.")

if __name__ == "__main__":
    main()

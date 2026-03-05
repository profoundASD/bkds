import os
import json

# Environment variable for the base directory
BKDS_NODEJS_PUBLIC = os.getenv("BKDS_NODEJS_PUBLIC", "/default/path/to/BKDS_NODEJS_PUBLIC")

# Input directory containing files to scan
INPUT_DIR = "/home/aimless76/Documents/Sync/BKDS/BKDS-APP/BKDS-NODEJS/public/data/content_feeds/"

def verify_image_paths(input_dir):
    """
    Scan .json files recursively for 'img_src' paths, verify their existence, and count missing files.

    Args:
        input_dir (str): Directory containing files to scan.

    Returns:
        dict: Summary with total paths, missing files, and missing file paths.
    """
    total_paths = 0
    missing_files = 0
    missing_file_paths = []

    for root, _, files in os.walk(input_dir):
        for file_name in files:
            if not file_name.endswith(".json"):
                continue  # Process only JSON files
            
            file_path = os.path.join(root, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading JSON file {file_path}: {e}")
                continue

            # Look for 'img_src' keys and verify their paths
            for item in extract_img_src(data):
                total_paths += 1
                normalized_path = os.path.join(BKDS_NODEJS_PUBLIC, item.lstrip("/"))
                
                # Verify existence case-sensitively
                if not os.path.exists(normalized_path):
                    missing_files += 1
                    missing_file_paths.append(normalized_path)

    return {
        "total_paths": total_paths,
        "missing_files": missing_files,
        "missing_file_paths": missing_file_paths
    }

def extract_img_src(data):
    """
    Recursively extract all 'img_src' paths from the JSON data.

    Args:
        data (dict or list): JSON data to scan.

    Returns:
        list: List of 'img_src' paths.
    """
    img_src_list = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "img_src" and isinstance(value, str):
                img_src_list.append(value)
            elif isinstance(value, (dict, list)):
                img_src_list.extend(extract_img_src(value))
    elif isinstance(data, list):
        for item in data:
            img_src_list.extend(extract_img_src(item))
    
    return img_src_list

def main():
    # Check if BKDS_NODEJS_PUBLIC is set correctly
    if not os.path.exists(BKDS_NODEJS_PUBLIC):
        print(f"Error: BKDS_NODEJS_PUBLIC does not exist or is not set correctly: {BKDS_NODEJS_PUBLIC}")
        return

    result = verify_image_paths(INPUT_DIR)

    print(f"Total image paths found: {result['total_paths']}")
    print(f"Missing files: {result['missing_files']}")
    if result['missing_files'] > 0:
        print("Missing file paths:")
        for path in result['missing_file_paths']:
            print(path)

if __name__ == "__main__":
    main()

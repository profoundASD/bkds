import os
import re
import json
import unicodedata
from datetime import datetime


def replace_aircraft_models(input_string):
    """
    Replaces common aircraft model patterns in the string with the more standard naming convention.

    Args:
    input_string (str): The string to process.

    Returns:
    str: The processed string with aircraft models corrected.
    """
    print('input_string before', input_string)
    # Dictionary of common aircraft models and their common misspellings
    aircraft_models = {
        "B 52": "B-52",
        "B  52": "B-52",
        "B52": "B-52",
        "B52": "B-52",
        "C 130": "C-130",
        "C  130": "C-130",
        "B 25": "B-25",
        "B25": "B-25",
        "B-25-Mitchell": "B-25 Mitchell",
        "KC 10": "KC-10",
        "KC  10": "KC-10",
        "B 1B" : "B-1B",
        "B 17" : "B-17",
        "B  17" : "B-17",
        "B17" : "B-17",
        "F 15" : "F-15",
        "F  15" : "F-15",
        "F15" : "F-15",
        "F 16" : "F-16",
        "F  16" : "F-16",
        "F16" : "F-16"
        # Add more models here as needed
    }

    # Replace each occurrence of the model in the string
    for model in aircraft_models:
        # Adjusting the regular expression to handle variations like "B 25G"
        pattern = rf'({model})\s?([A-Z0-9]+)?'
        replacement = lambda m: aircraft_models[m.group(1)] + ('-' + m.group(2) if m.group(2) else '')
        input_string = re.sub(pattern, replacement, input_string)
    print('input_string after', input_string)
    input_string = strip_image_size_strings(input_string)
    return input_string

def strip_unwanted_characters(input_string):
    """
    Strips unwanted characters and patterns from the input string while preserving original spaces.
    
    Args:
    input_string (str): The string to process.

    Returns:
    str: The processed string.
    """
    # Remove strings of 4 or more sequential numbers
    input_string = re.sub(r'\d{4,}', '', input_string)

    # Replace underscores and dashes with spaces (to preserve original spaces)
    input_string = re.sub(r'[_\-]', ' ', input_string)

    # Remove specific unwanted characters and patterns
    characters_to_remove = "[()`,:?]|640px|\.jpg|\.png|\.svg"
    input_string = re.sub(characters_to_remove, '', input_string)

    # Replace multiple spaces with a single space
    input_string = re.sub(r'\s+', ' ', input_string)
    
    return input_string.strip()



def normalize_string(input_string):
    """
    Normalizes the given string to ASCII characters, removing accents, special characters,
    as well as new lines, commas, apostrophes, spaces, and hyphens, and replaces spaces and hyphens with underscores.

    Args:
    input_string (str): The string to normalize.

    Returns:
    str: The normalized string.
    """
    # Normalize to ASCII, ignoring non-ASCII characters
    normalized_string = unicodedata.normalize('NFD', input_string).encode('ascii', 'ignore').decode('ascii')

    # Remove new lines, commas, apostrophes, and replace spaces and hyphens with underscores
    normalized_string = normalized_string.replace('\n', '').replace(',', '').replace("'", '').replace(" ", "_").replace('-', '_')

    return normalized_string

def generate_metadata(directory):
    metadata = []
    for group_name in os.listdir(directory):
        group_path = os.path.join(directory, group_name)
        if os.path.isdir(group_path):
            for type_name in os.listdir(group_path):
                type_path = os.path.join(group_path, type_name)
                if os.path.isdir(type_path):
                    img_details = []
                    sequence_number = 1  # Initialize sequence number for each group_name
                    for img_file in os.listdir(type_path):
                        if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            normalized_img_file = normalize_string(img_file)
                            # Formatting file name and appending sequence number before extension
                            file_name, file_extension = os.path.splitext(img_file)
                            formatted_file_name = type_name.replace(')', '').replace('(', '').replace(' ', '_').replace('-', '_').replace('#', '_')
                            file_name_with_sequence = f"{formatted_file_name}_{sequence_number}{file_extension}"

                            img_detail = {
                                "IMG": normalized_img_file,
                                "FILE_NAME": normalize_string(file_name_with_sequence),
                                "KEYWORDS": [
                                    strip_image_size_strings(replace_aircraft_models(strip_unwanted_characters(normalize_string(group_name)))), 
                                    strip_image_size_strings(replace_aircraft_models(strip_unwanted_characters(type_name))), 
                                    strip_image_size_strings(replace_aircraft_models(strip_unwanted_characters(normalize_string(file_name))))
                                ]
                            }
                            img_details.append(img_detail)
                            sequence_number += 1  # Increment sequence number
                    if img_details:
                        metadata.append({
                            "IMG_PATH": directory,
                            "GROUP_NAME": group_name,
                            "ACCESS_NAME_ALT": type_name.replace('_', ' ').replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace('.svg', ''),
                            "ACCESS_NAME": type_name,
                            "IMG_DETAIL": img_details
                        })
    return metadata


def strip_image_size_strings(input_string):
    """
    Strips common image size strings from the input string.

    Args:
    input_string (str): The string to process.

    Returns:
    str: The processed string.
    """
    size_strings = [
        "640px", "800px", "1024px", "1280px",
        "1920px", "300px", "600px", "1200px",
        "1600px", "2048px"
    ]
    for size_string in size_strings:
        input_string = input_string.replace(size_string, '')
    
    return input_string

def main():
    print('main')
    # Expand environment variables in the path
    directory = os.path.expandvars("/home/aimless76/Documents/Sync/BKDS/BKDS_APP/tmp-data")
    # Generate metadata
    metadata = generate_metadata(directory)
    # Timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"../data/output/metadata_{timestamp}.json"

    # Write metadata to a file
    with open(output_filename, 'w') as file:
        json.dump(metadata, file, indent=4)

    print(f"Metadata written to {output_filename}")

# Example usage
# main()

# Note: Replace "/path/to/your/directory" with the actual directory path or an environment variable.
# Make sure to run main() to execute the script.
main()
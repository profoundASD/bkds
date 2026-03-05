import json
import glob
import os
import re

def read_latest_json_file(directory_pattern):
    """
    Reads the latest JSON file based on the specified pattern.

    Args:
    directory_pattern (str): The pattern to search for JSON files.

    Returns:
    str: The content of the latest JSON file.
    """
    list_of_files = glob.glob(directory_pattern)
    if not list_of_files:
        return None

    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, 'r') as file:
        json_data = file.read()
    
    return json_data

def strip_number_hyphen_sequences(input_string):
    # Regex to find sequences of numbers and hyphens longer than 5 characters
    return re.sub(r'[\d-]{6,}', '', input_string)

def generate_bash_script_from_json(json_data):
    data = json.loads(json_data)
    bash_script = "#!/bin/bash\n\n"

    for group in data:
        access_name = group['ACCESS_NAME']
        group_name = group['GROUP_NAME']

        for img_detail in group['IMG_DETAIL']:
            img_name = img_detail['IMG'].replace('\n', '')  # Remove new lines from the file name
            new_file_name = img_detail['FILE_NAME']  # Get the new file name from IMG_DETAIL
            img_path = os.path.join(group['IMG_PATH'], group_name, access_name, img_name).replace('\n', '')  # Get the full path of the image

            # Extract the file extension from the new file name
            file_extension = os.path.splitext(new_file_name)[-1].lstrip('.')

            # Generate the new file path
            new_file_path = os.path.join('../data/output/Aviation', group_name, access_name, new_file_name).replace('\n', '')

            # Create the directory if it does not exist
            target_directory = os.path.dirname(new_file_path).replace('\n', '')  # Strip newline characters
            bash_script += f'mkdir -p "{target_directory}"\n'
            img_path=img_path.replace('\n', '') 
            new_file_path=new_file_path.replace('\n', '')
            # Create the bash command to copy the file, using double quotes
            bash_script += f'cp "{img_path}" "{new_file_path}"\n'

    return bash_script


# Read the latest JSON data
json_data = read_latest_json_file('../data/output/metadata_*.json')

if json_data:
    bash_script = generate_bash_script_from_json(json_data)
    # Write the bash script to a file
    with open('../data/output/bkds_mass_move.sh', 'w') as file:
        file.write(bash_script)
    print("Bash script generated and saved to '../data/output/bkds_mass_move.sh'")
else:
    print("No JSON files found in the specified pattern.")


"""
Build BKDS Subject Index File

This program reads a JSON file containing subject IDs and searches for matching subject IDs in a directory containing *_subj.json files. It then creates an output file with matching entries, including file paths and timestamps. The main steps include:

1. Parse command-line arguments: The program accepts batch ID, a JSON file containing subjIDs, and a directory containing *_subj.json files as input arguments.
2. Read subjIDs data: The program reads subjIDs from the specified JSON file and normalizes them for case-insensitive matching.
3. Search for matching entries: It iterates through the files in the specified directory, checks if they end with '_subj.json', and searches for matching subjIDs in each file.
4. Write output: The program saves the matching entries to an output JSON file with a timestamp.
5. Log messages: Throughout the process, the program logs messages, including status updates and errors.

Usage:
python script.py <batch_id> <subj_id_json_file> <subj_path>

Arguments:
- batch_id: The batch ID for processing.
- subj_id_json_file: Path to the JSON file containing subjIDs.
- subj_path: The directory containing *_subj.json files to search.

Example:
python script.py 1234 subj_ids.json /path/to/subj_files
"""

import json
import sys
import os
from bkdsLogMsg import log_msg
import argparse
from datetime import datetime
import time
# BKDS-NODEJS/public/data/config/bkds_subj_index.json
#####################################################################
# Main Setup / Variables

env_path = 'BKDS_NODEJS_PUBLIC'
out_dir = os.getenv(env_path)

# Define the output file path
output_dir = os.getenv('BKDS_NODEJS_PUBLIC', '')  # Use the BKDS_NODEJS_DATA environment variable
output_file = os.path.join(output_dir, 'data', 'output', 'bkds_subj_index_wip.json')

def parse_args():
    parser = argparse.ArgumentParser(description="Process entries.")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("subj_id_json_file", help="JSON file containing subjIDs")
    parser.add_argument("subj_path", help="Directory containing *_subj.json files")

    # Parse the command-line arguments
    return parser.parse_args()

args = parse_args()
batch_id = args.batch_id
subj_id_json_file_path = args.subj_id_json_file
subj_path = args.subj_path  # Directory containing *_subj.json files

print(f'subj_path {subj_path}')
print(f'subj_id_json_file {subj_id_json_file_path}')
print(f'batch_id {batch_id}')

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_GET_SUBJ_INDEX', msg)
    print(msg)

def normalize_subj_id(subj_id):
    # Remove leading/trailing whitespace and decode to ensure consistent encoding
    return subj_id.strip().encode('utf-8').decode('utf-8').lower()

def process_entries(batch_id, subj_id_json_file_path, subj_path):
    logMsg(f"process_entries for {batch_id}: using subj_id_json_file {subj_id_json_file_path}")
    
    # Read subjIDs from the JSON file
    with open(subj_id_json_file_path, 'r') as subj_id_json_file:
        subj_ids_data = json.load(subj_id_json_file)

    subj_ids = []

    if isinstance(subj_ids_data, dict) and 'subjID' in subj_ids_data:
        print('is instance dict')
        subj_ids_data = subj_ids_data['subjID']  # Get the list of subjIDs

    if isinstance(subj_ids_data, list):
        print('is instance list')
        for entry in subj_ids_data:
            print(f'processing_entry {entry}')
            normalized_subj_id = normalize_subj_id(entry)
            subj_ids.append(normalized_subj_id)  # Normalize for case-insensitive matching

    print(f'subj_ids: {subj_ids}')

    matching_entries = []

    # Print all files in the subj_path directory
    for filename in os.listdir(subj_path):
        print(f'file name avail {filename}')

    # Search for *_subj.json files in the specified directory
    for filename in os.listdir(subj_path):
        print(f'Checking filename {filename}')
        if filename.endswith('_subj.json'):
            print(f'subj.json found {filename}')
            full_file_path = os.path.join(subj_path, filename)  # Full path to the file
            with open(full_file_path, 'r') as json_file:
                data = json.load(json_file)
                
                if isinstance(data, list):
                  #  print('File is a list:', full_file_path)
                    for entry in data:
                        print('Entry:', entry)
                        if 'subjID' in entry:
                            normalized_subj_id = normalize_subj_id(entry['subjID'])
                            print('Normalized subjID:', normalized_subj_id)
                            print('Matching against subj_ids:', subj_ids)
                            if normalized_subj_id in subj_ids:
                                print(f'subjID matched: {entry["subjID"]}')
                                # Extract the timestamp from the filename
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                matching_entries.append({
                                    "subj_id": entry['subjID'],
                                    "file_path": full_file_path,
                                    "time_stamp": timestamp,
                                    "entry": entry
                                })


    return matching_entries

def main():
    matching_entries = process_entries(batch_id, subj_id_json_file_path, subj_path)

    # Write the matching entries to the output file
    with open(output_file, 'w') as output:
        json.dump(matching_entries, output, indent=4)

    logMsg(f"Matching entries saved to {output_file}")

if __name__ == "__main__":
    main()

"""
Build BKDS Subject Index File

This program reads an index file of subject insights to target and builds a file for the next step. The main steps include:

1. Parse command-line arguments: The program accepts a batch ID and a keyword (or '*' for all keywords) as input arguments.
2. Read index data: The program reads data from the specified index file, which contains information about keywords and file paths.
3. Process data: It searches for entries in the index data that match the provided keyword or all keywords. For each matching entry, it extracts the file path and appends a timestamp.
4. Write output: The program saves the matching entries to an output file, which can be used in the next step of processing.
5. Log messages: Throughout the process, the program logs messages, including status updates and errors.

Usage:
python script.py <batch_id> <keyword>

Arguments:
- batch_id: The batch ID for processing.
- keyword: The keyword to filter entries from the index file. Use '*' to include all entries.

Example:
python script.py 1234 waterfalls
"""

import json
import sys
import os
from bkdsLogMsg import log_msg
import argparse
from datetime import datetime

# BKDS-NODEJS/public/data/config/bkds_subj_index.json
#####################################################################
# Main Setup / Variables

env_path = 'BKDS_NODEJS_PUBLIC'
out_dir = os.getenv(env_path)
index_file = 'bkds_subj_index.json'
index_file = os.path.join(out_dir, 'data', 'config', index_file)
print(f'index file {index_file}')

# Define the output file path
output_dir = os.getenv('BKDS_NODEJS_PUBLIC', '')  # Use the BKDS_NODEJS_DATA environment variable
output_file = os.path.join(output_dir, 'data', 'output', 'bkds_subj_index_wip.json')

parser = argparse.ArgumentParser(description="Process entries.")
parser.add_argument("batch_id", help="Batch ID")
parser.add_argument("keyword", help="Keyword or '*' for all")

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_GET_SUBJ_INDEX', msg)
    print(msg)

def process_entries(batch_id, keyword):
    logMsg(f"process_entries for {batch_id}: keyword= {keyword}")
    print(f'filename: {index_file}')
    with open(index_file) as file:
        data = json.load(file)

    print(f'data: {data}')

    matching_entries = []

    if data and isinstance(data, list):  # Check if data is a non-empty list
        data_dict = data[0]  # Access the dictionary within the list
        for key, value in data_dict.items():
            print(f'key, value: {key}, {value}')
            if value.endswith(f'bkds_{keyword}_subj.json'):
                # Extract the timestamp from the filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                matching_entries.append({
                    "file_path": value,
                    "time_stamp": timestamp
                })

    return matching_entries

def main(args):
    batch_id = args.batch_id
    keyword = args.keyword

    matching_entries = process_entries(batch_id, keyword)

    # Write the matching entries to the output file
    with open(output_file, 'w') as output:
        json.dump(matching_entries, output, indent=4)

    logMsg(f"Matching entries saved to {output_file}")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)

import os
import sys
import json
import argparse
from datetime import datetime
import time
import re
from bkdsFlickrAPI import getFlickrData
from bkdsUtilities import genInsightID, logMsg, subjGenOutputHandler

bkds_util_python = os.environ.get('BKDS_UTIL_PYTHON')
if bkds_util_python:
    print("set BKDS_UTIL_PYTHON ")
    sys.path.append(bkds_util_python)
else:
    print("BKDS_UTIL_PYTHON environment variable is not set.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("json_filepath", help="Path to the JSON file containing data to process")
    return parser.parse_args()

def main():
    args = parse_arguments()
    batch_id = args.batch_id
    json_filepath = args.json_filepath
    subjType = 'flickr'
    output_prefix = 'bkds_subj_gen'
    output_type = 'json'

    with open(json_filepath, 'r') as file:
        json_data = json.load(file)

    output_data = []
    processed_terms = set()

    for item in json_data:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        subjID = item['subj_id']
        entry = item['entry']
        keyword = entry['keyword']
        category = entry['category']
        logMsg(f'processing {keyword} for {category}')

        if keyword not in processed_terms:
            images = getFlickrData(keyword, 10, os.getenv("FLICKR_API_KEY"))
            insightID = genInsightID(keyword, subjID, category)
            result_item = {
                "searchTerm": keyword,
                "insightID": insightID,
                "subjID": subjID,
                "Images": images,
                "category": category,
                "collection_date": timestamp
            }
            output_data.append(result_item)
            processed_terms.add(keyword)

        output_filepath = subjGenOutputHandler(os.getenv('BKDS_NODEJS_SUBJGEN'), output_data, subjType, output_prefix, output_type, keyword, subjID, timestamp)

        print(f"Saved results to {output_filepath}")

if __name__ == "__main__":
    main()

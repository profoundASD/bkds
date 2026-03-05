"""
Central Controller Script for Subject Processing

This script acts as a central controller for processing data related to different subjects (Wikipedia, Flickr, YouTube).
It utilizes custom modules for each subject type and dynamically handles processing based on the specified subject type.
The script facilitates batch processing by reading JSON data and supports configuration through command line arguments.

Features:
- Reads JSON data for subject processing.
- Delegates processing to specific modules based on subject type ('wiki', 'flickr', 'youtube').
- Supports configurable batch ID, JSON filepath, output prefix, and file type through command line arguments.
- Logs significant events and errors.

Usage:
python [script_name].py [batch_id] [json_filepath] [output_prefix] [output_type] [subjType]

Dependencies:
- bkdsUtilities for logging and utility functions.
- bkds_subjGenWikiMain, bkds_subjGenFlickrMain, bkds_subjGenYouTubeMain for subject-specific processing.

Note: Ensure 'BKDS_UTIL_PYTHON' environment variable is set for custom module imports.
"""
import os
import sys
import argparse
from bkdsUtilities import log_msg
from bkds_subjGenWikiMain import subjGenWiki
from bkds_subjGenFlickrMain import subjGenFlickr
#from bkds_subjGenYouTubeMain import subjGenYouTube

#####################################################################
# Main Setup / Variables
import json

print("Raw command-line arguments:", sys.argv)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("output_prefix", help="Output prefix")
    parser.add_argument("output_type", help="Output file type")
    parser.add_argument("subjType", help="Subject type ('wiki', 'flickr', 'youtube')")
    return parser.parse_args()

def read_sql_query_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data['sql_query']

args = parse_arguments()
print("Received arguments:", args)  # Print the received arguments for debugging

batch_id = args.batch_id
output_prefix = args.output_prefix
output_type = args.output_type
subjType = args.subjType

query_file = "../sql/bkds_subject_index_source_query.json"  # Path to the JSON query file
sql_query = read_sql_query_from_json(query_file)
print("SQL Query:", sql_query)  # Print the SQL query for debugging

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), batch_id, msg)
    print(msg)

    

# Database Query Function
def main():
    logMsg("in subjGen main")

    if subjType == 'wiki':
        logMsg("processing wiki")
        subjGenWiki(sql_query, output_prefix, output_type, subjType)
    elif subjType == 'flickr':
        logMsg("processing flickr")
        subjGenFlickr(sql_query, output_prefix, output_type, subjType)
    elif subjType == 'youtube':
        logMsg("processing youtube")
        #subjGenYouTube(data, output_prefix, output_type, subjType)        
    else:
        logMsg(f"Unsupported subject type: {subjType}")

if __name__ == "__main__":
    main()
"""
Script Name: [Script Name]
Description: This script automates the process of loading JSON data into a PostgreSQL database. 
It supports different data sources like Flickr, YouTube, and Wiki. The script reads JSON files 
from a specified directory, matches them against a given pattern, and then processes each file 
according to its data source type. The data is then inserted into the appropriate database tables 
based on a dynamic template mapping system.

Author: [Your Name]
Date: [Creation or Last Modification Date]
"""

import json
import os
import glob
import argparse
from datetime import datetime
import time

# Custom utility functions
from bkds_Utilities import log_msg, getHash, getDBConn, closeDB, archiveData, load_column_mappings


########################################################################
#  Main logic and functions
def logMsg(msg):
    log_msg(program_name, f'BKDS_UTIL_LOGMSG', msg)
    print(msg)


# Script configuration and argument parsing
parser = argparse.ArgumentParser(description="Load JSON data into PostgreSQL database.")
parser.add_argument("directory", help="env dir")
parser.add_argument("subj_type", help="data type (youtube, flickr, wiki, etc)")
args = parser.parse_args()

# Main variables setup
proc_dir = args.directory
subj_type = args.subj_type

program_name = os.path.basename(__file__)
batch_id = 'SUBJ_GEN_MAIN'

mapping_file = 'bkds_data_mappings.json'
mapping_env = os.getenv('BKDS_UTIL_DATA')
mapping_dir = os.path.join(mapping_env, 'config', mapping_file)

output_type='json'
data_env = os.getenv(proc_dir)



data_dir = os.path.join(data_env, subj_type, 'output', output_type)

file_pattern = subj_type

logMsg(f'using\n')
logMsg(f'data_dir: {data_dir}')
logMsg(f'proc_dir: {proc_dir}')
logMsg(f'subj_type: {subj_type}')
logMsg(f'output_type: {output_type}')
logMsg(f'file_pattern: {file_pattern}')

#data keys
wiki_key = "wiki"
yt_key = "youtube"
flickr_key = "flickr"
data_src_key = "dataSource"
template_key = "bkds_subjGen_load"

src_key = 'dataSource'
api_key = 'api_results'
#templateKey = 'subjGen_insertData'

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getInsertTemplate(dataSource):  
    return load_column_mappings(f"{template_key}_{dataSource}")

def generateInsertStatements(json_data, data_source_type):
    print(f"generateInsertStatements with: {data_source_type}")
    data_to_insert = []
    
    #api result fields to load
    subjectID = json_data.get("subjectID", "")
    searchID = json_data.get("searchID", "")
    resultID = json_data.get("resultID", "")
    insightID = json_data.get("insightID", "")
    category = json_data.get("category", "")
    searchTerm = json_data.get("searchTerm", "")
    utcTime = json_data.get("utcTime", "")

    #load maintenance fields
    load_id = getHash((searchID or "") + (utcTime or ""))

    load_date=timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    load_job=f'{program_name}'

    for api_result in json_data.get("api_results", []):
        logMsg(f"handling api_result {api_result}")
        if data_source_type == flickr_key:
            imageUrl = api_result
            resultID = getHash((api_result or "") + (resultID or ""))
            data_to_insert.append((subjectID, searchID, resultID, insightID, category, searchTerm, imageUrl, utcTime, load_id, load_date, load_job))
        elif data_source_type == wiki_key:

            wiki_result_id = api_result.get("wiki_result_id", "")
            subjTitle = api_result.get("subjTitle", "")
            pageURL = api_result.get("pageURL", "")
            extract = api_result.get("extract", "")
            images = api_result.get("images", [])


            logMsg(f'wiki_result_id: {wiki_result_id}')
            logMsg(f'subjTitle: {subjTitle}')
            logMsg(f'pageURL: {pageURL}')
            logMsg(f'extract: {extract}')
            if not images:  # Check if the images list is empty
                logMsg(f"No images found for wiki_result_id: {wiki_result_id}")
                resultID = getHash((resultID or "") + (wiki_result_id or ""))
                data_to_insert.append((subjectID, searchID, resultID, insightID, category, searchTerm, wiki_result_id, subjTitle, pageURL, extract, "", utcTime, load_id, load_date, load_job))
            else:
                for image_url in images:
                    logMsg(f"handling image_url: {image_url}")
                    resultID = getHash((image_url or "") + (resultID or "") + (wiki_result_id or ""))
                    data_to_insert.append((subjectID, searchID, resultID, insightID, category, searchTerm, wiki_result_id, subjTitle, pageURL, extract, image_url, utcTime, load_id, load_date, load_job))

        elif data_source_type == yt_key:
            title = api_result.get("title", "")
            description = api_result.get("description", "")
            thumbnail = api_result.get("thumbnail", "")
            videoUrl = api_result.get("url", "")
            timestamp = api_result.get("timestamp", "")
            resultID = getHash((videoUrl or "") + (resultID or ""))
            data_to_insert.append((subjectID, searchID, resultID, insightID, category, searchTerm, title, description, thumbnail, videoUrl, timestamp, utcTime, load_id, load_date, load_job))

    insert_query = getInsertTemplate(data_source_type)
    print(f'insert_query: {insert_query}\n\n')  
    
    conn, cursor = getDBConn()
    print(f'\n{data_to_insert}\n')
    conn.executemany(insert_query, data_to_insert)
    cursor.commit()
    closeDB(cursor, conn)

    return data_to_insert


def loadDB(directory, pattern):
    logMsg(f"starting loadDB main in {program_name} for dir: {directory}")
    # Ensure pattern includes wildcard characters if needed
    wildcard_pattern = f'*{pattern}*' if '*' not in pattern else pattern
    logMsg(f'wildcard_pattern: {wildcard_pattern}\n directory: {directory}')
    #print(f'Searching in directory: {directory} for pattern: {wildcard_pattern}')
    processed_files = []  # List to keep track of processed files
    for file_path in glob.glob(os.path.join(directory, wildcard_pattern)):
        logMsg(f"handling: {file_path}")
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                for item in data:
                    generateInsertStatements(item, item.get(data_src_key, "").lower())  
            #print(f"Successfully processed file: {file_path}")
            processed_files.append(file_path)  # Add file to the list of processed files
        except Exception as e:
            logMsg(f"Error processing file {file_path}: {e}")
    # Archive processed files if there are any
    if processed_files:
        archiveData(processed_files, directory)

if __name__ == "__main__":
    logMsg(f"starting main in {program_name}\nargs: {args}\nfile_pattern: {file_pattern}")

    loadDB(data_dir, file_pattern)

    logMsg(f"finished main in {program_name} with {args}")
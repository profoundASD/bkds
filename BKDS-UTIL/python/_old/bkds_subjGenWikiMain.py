"""
Wikipedia Subject Generation Script

This script processes a JSON file containing search searchTerms for Wikipedia, retrieves relevant 
page data, images, and extracts, and compiles these into a structured format. 
It is tailored to manage multiple searchTerms, avoid redundant searches, and systematically 
organize the results with detailed insights.

Features:
- Reads searchTerms from a JSON file for Wikipedia page searches.
- Utilizes Wikipedia API to fetch page data, including titles, URLs, images, and page extracts.
- Generates unique insight IDs for each searchTerm.
- Compiles fetched data into a structured output, including key information about the Wikipedia pages.
- Saves the processed data in a specified format with a timestamped filename.
- Supports configurable output prefix and file type.
- Implements an interval delay between processing each searchTerm for efficient usage of resources.
- Logs processing activities and errors for tracking and debugging.
- Now supports optional direct JSON data input from a calling program, along with the existing functionality of reading from a JSON file.
- Introduces a new `--altSource` flag to specify a file path for input JSON data.

Usage:
- If using a JSON file: Execute `subjGenWiki --altSource <json_filepath>` with the output prefix, output type, and subject type ('wiki').
- If using JSON data from a calling program: Execute `subjGenWiki` with JSON data passed as an argument, along with the output prefix, output type, and subject type.

"""
from datetime import datetime
import time
import os
import argparse
#custom functions
from bkds_subjGenWikiAPI import getWikiData, getPageExtract, getPageImages
from bkdsUtilities import genInsightID, log_msg, subjGenOutputHandler, fetch_data, load_data_to_table

#####################################################################
# Main Setup / Variables
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process Wikipedia subjects")
    parser.add_argument("sql_query", help="sql_query containing the data")
    parser.add_argument("output_prefix", help="Output prefix")
    parser.add_argument("output_type", help="Output file type")
    parser.add_argument("subjType", help="Subject type ('wiki')")
    return parser.parse_args()

args = parse_arguments()

program_name = os.path.basename(__file__)
batch_id='SUBJ_GEN_WIKI_MAIN'

target_schema='dev'
target_obj='stg_wiki_subjGen'
target_table=f'{target_schema}.{target_obj}'

title_key='title'
category_key='category'
url_key='wiki_url'

rec_key='record_id'
search_key='search_id'
search_term_key='search_term'

api_wait = 2
output_files = []

########################################################################
#  Main logic and functions
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def subjGenWiki(sql_query, output_prefix, output_type, subjType):
    logMsg(f'started {program_name}')

    subjects = fetch_data(sql_query)
    for item in subjects:
        #print(f'processing {item} in subjects for {search_key}')
        if search_key in item:
            print(f'found {search_key} in {item}')
            searchTerm = item[search_term_key]
            insightID = item[rec_key]
            searchID = item[search_key]

            logMsg(f"Processing: {insightID} with {searchTerm}")
            search_results = getWikiData(searchTerm)

            for result in search_results:
                pageTitle = result.get(title_key, '')
                category = item.get(category_key, '')
                searchURL = result.get(url_key, '')
                
                images = getPageImages(pageTitle)
                time.sleep(api_wait)
                extract = getPageExtract(pageTitle)

                resultID = genInsightID(searchTerm, searchURL, searchID)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                output_data = {
                    "searchID" : searchID,
                    "resultID" : resultID,
                    "insightID": insightID,
                    "category": category,
                    "searchTerm": searchTerm,
                    "subjTitle": pageTitle,
                    "pageURL": searchURL,
                    "images": images,
                    "extract": extract,
                    "utcTime": timestamp
                }

                out_file = subjGenOutputHandler(output_data, subjType, output_prefix, output_type, searchTerm, insightID, timestamp)
                logMsg(f"Ouptut written to {out_file} from {program_name} for {insightID}")

                output_files.append(out_file)
                time.sleep(api_wait)

        else:
            logMsg("Entry key not found in database item.")


    if output_files:
        for file_path in output_files:
            logMsg(f"Loading to {target_table} with {file_path} from {program_name}")
            load_data_to_table(file_path, target_table)
    else:
        logMsg(f"No files to load to {target_table} from {program_name} ")            

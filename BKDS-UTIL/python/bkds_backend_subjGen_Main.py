"""
Arguments:

batch_id: The batch ID for the processing session.
subjType: The subject type to process ('wiki', 'flickr', 'youtube').
Dependencies:

bkds_Utilities: Contains utility functions for logging, data fetching, ID generation, and output handling.
bkds_backend_subjGen_API_Wiki: Module for fetching and processing Wikipedia data.
bkds_backend_subjGen_API_Flickr: Module for fetching and processing Flickr data.
bkds_backend_subjGen_API_YouTube: Modules for fetching and processing YouTube data.
Notes:

Ensure the BKDS_UTIL_PYTHON environment variable is set correctly for custom module imports.
Adjust the api_wait variable if API rate limits or response times change.
The script replaces a placeholder in the SQL query with the provided subject type to fetch relevant data.


Arguments:

batch_id: The batch ID for the processing session.
subjType: The subject type to process ('wiki', 'flickr', 'youtube').

Dependencies:

bkds_Utilities: Contains utility functions for logging, data fetching, ID generation, and output handling.
bkds_backend_subjGen_API_Wiki: Module for fetching and processing Wikipedia data.
bkds_backend_subjGen_API_Flickr: Module for fetching and processing Flickr data.
bkds_backend_subjGen_API_YouTube: Modules for fetching and processing YouTube data.

Notes:

Ensure the BKDS_UTIL_PYTHON environment variable is set correctly for custom module imports.
Adjust the api_wait variable if API rate limits or response times change.
The script replaces a placeholder in the SQL query with the provided subject type to fetch relevant data.

USAGE: python [script_name].py [batch_id] [subjType]

"""

import os
import json
import argparse
from datetime import datetime
import time

#custom functions
from bkds_Utilities import log_msg, fetch_data, genInsightID, subjGenOutputHandler, get_sqlTemplate
from bkds_backend_subjGen_API_Wiki import getWikiData
from bkds_backend_subjGen_API_Flickr import getFlickrData
from bkds_backend_subjGen_API_YouTube import getYouTubeData, getVideoData
#####################################################################
# Main Setup / Variables

program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("subjType", help="Subject type ('wiki', 'flickr', 'youtube')")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
subjType = args.subjType

query_key = 'bkds_subjGen_source_index_wip'
print(f'query_key {query_key}')

subj_key='subject_id'
rec_key='insight_id'
search_key='search_id'
category_key='data_category'
search_term_key='search_term'

output_prefix='bkds_subjGen_'
output_type='json'

batch_id=f'{batch_id}_MAIN'
api_wait = 3

########################################################################
#  Main logic and functions
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getMedia(searchTerm):
    logMsg(f"starting getMedia with {searchTerm}")
    try:
        media_data = []
        if subjType == 'youtube' or subjType == 'yt':
            media_data = getVideoData(getYouTubeData(searchTerm))
        elif subjType == 'flickr':
            media_data = getFlickrData(searchTerm, 10)
        elif subjType == 'wiki':
            media_data = getWikiData(searchTerm)
        return media_data
    except Exception as e:
        logMsg(f"Error in getMedia for '{searchTerm}' with type '{subjType}': {str(e)}")
        return []

def subjGenMedia(sql_query, subjType):
    logMsg(f"starting subjGenMedia with {subjType} and {sql_query}")
    data = fetch_data(sql_query)  # Fetch data using the SQL query

    output_data = []
    processed_terms = set()

    for item in data:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        insightID = item[rec_key]
        searchTerm = item[search_term_key]
        searchID = item[search_key]
        category = item[category_key]
        subjectID= item[subj_key]
        logMsg(f'Processing {searchTerm} for {category}')

        if searchTerm not in processed_terms:
            
            media_results = getMedia(searchTerm)
            resultID = genInsightID(subjectID, insightID, timestamp)
            print(f'using media_results:\n{json.dumps(media_results)[:150]}')  # Print first 150 characters
            #print(f'using media_results:\n{media_results}')
            #time.sleep(5)
            result_item = {
                "searchID" : searchID,
                "subjectID" : subjectID,
                "resultID" : resultID,
                "insightID": insightID,
                "category": category,
                "dataSource": subjType,
                "searchTerm": searchTerm,
                "api_results": media_results,
                "utcTime": timestamp
            }
            output_data.append(result_item)
            processed_terms.add(searchTerm)

        output_filepath = subjGenOutputHandler(output_data, subjType, output_prefix, output_type, searchTerm, insightID)
        logMsg(f"Results from subjGenMedia output: {output_filepath}")
        output_data=[]
        time.sleep(api_wait)

# Database Query Function
def main():
    logMsg(f"starting main for {batch_id} for {subjType} from {program_name}")
    sql_query = get_sqlTemplate(query_key)

    # Replace {api_source} with subjType in the SQL query
    if subjType:
        print(f'using sql_query {sql_query}')
        
        sql_query = sql_query.replace("api_source", subjType)
        print(f'using sql_query {sql_query}')
        
        logMsg(f"processing {subjType} with {sql_query}")
        subjGenMedia(sql_query, subjType)     
    else:
        logMsg(f"Unsupported subject type: {subjType}")
    
    logMsg(f"ending main for {batch_id} from {program_name}")

if __name__ == "__main__":
    main()

import os
import sys
import time
from datetime import datetime
# Custom functions
from bkds_subjGenYouTubeAPI import getYouTubeData, getVideoData
from bkds_subjGenFlickrAPI import getFlickrData
from bkdsUtilities import genInsightID, log_msg, subjGenOutputHandler, fetch_data

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id = f'SUBJ_GEN_{sys.argv[1]}_MAIN'  # Generalized batch ID

rec_key = 'record_id'
search_key = 'search_id'
category_key = 'category'
search_term_key = 'search_term'

api_wait = 3

########################################################################
#  Main logic and functions
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def subjGenMedia(sql_query, output_prefix, output_type, subjType):
    data = fetch_data(sql_query)  # Fetch data using the SQL query

    output_data = []
    processed_terms = set()

    for item in data:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        insightID = item[rec_key]
        searchTerm = item[search_term_key]
        searchID = item[search_key]
        category = item[category_key]
        logMsg(f'Processing {searchTerm} for {category}')

        if searchTerm not in processed_terms:
            resultID = genInsightID(searchTerm, insightID, timestamp)
            media_data = []

            if subjType == 'youtube':
                media_data = getVideoData(getYouTubeData(searchTerm))
            elif subjType == 'flickr':
                media_data = getFlickrData(searchTerm, 10)
            
            result_item = {
                "searchID" : searchID,
                "resultID" : resultID,
                "insightID": insightID,
                "category": category,
                "searchTerm": searchTerm,
                "Media": media_data,
                "utcTime": timestamp
            }
            output_data.append(result_item)
            processed_terms.add(searchTerm)

        output_filepath = subjGenOutputHandler(output_data, subjType, output_prefix, output_type, searchTerm, insightID, timestamp)
        logMsg(f"Results output: {output_filepath}")
        time.sleep(api_wait)

# Example Usage
if __name__ == "__main__":
    sql_query = "YOUR_SQL_QUERY"
    output_prefix = "media_output"
    output_type = "json"
    subjType = "youtube"  # or 'flickr'

    subjGenMedia(sql_query, output_prefix, output_type, subjType)
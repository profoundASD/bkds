import json
import os
import glob
import argparse
from datetime import datetime
import argparse

#custom functions
from bkdsUtilities import log_msg, getHash, get_sqlTemplate, getDBConn, closeDB, getHash, archiveData

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id=f'SUBJ_GEN__MAIN'

src_key='dataSource'
api_key='api_results'
templateKey = 'subjGen_insertData'

#for archiving processed data
archive_name='bkds_SubjGen'
archive_dir='archive'

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getInsert(dataSource):  
    template_prefix='subjGen_insertData'
    templateKey=f"{template_prefix}_{dataSource}"
    sql_query = get_sqlTemplate(templateKey)
    return sql_query

def subjGen_insertData(cursor, json_data, load_id, load_date, load_job, dataSource):
    logMsg(f"starting subjGen_insertData with {load_id} for {dataSource}")

    column_mapping = {
        "flickr": ['searchID', 'resultID', 'insightID', 'category', 'dataSource','searchTerm', 'utcTime'],
        "flickr_url":  ['searchID', 'resultID', 'insightID', 'img_url'],
        "youtube": ['searchID', 'resultID', 'insightID','category',
                    'dataSource','searchTerm','description','title','url',
                    'thumbnail','timestamp'],
        "wiki": ['searchID', 'wiki_result_id', 'resultID', 'insightID', 'category', 'dataSource', 'searchTerm',
                 'extractData', 'subjTitle', 'pageURL', 'utcTime'],
        "wiki_url": ['searchID', 'wiki_result_id', 'resultID', 'insightID', 'img_url']
    }

    record_id = getHash(json.dumps(json_data))  # Unique identifier

    columns = column_mapping[dataSource]
    json_values = tuple(json_data.get(key, '') for key in columns)

    data_values = (record_id,) + json_values + (load_id, load_date, load_job)
    print(f'json_values\n{json_values}')
    print(f'data_values\n{data_values}')

    sql_query = getInsert(dataSource)
    print(f'sql_query_final {sql_query}')
    if sql_query and data_values:
        cursor.execute(sql_query, data_values)

def loadSubjGenData(dataSource, items):
    logMsg(f"starting loadSubjGenData for dataSource: {dataSource}")
    load_date = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    load_id = getHash(load_date)
    load_job = 'loadSubjGenData'

    conn, cursor = getDBConn()

    for item in items:
        # Extract top-level attributes
        topLevelAttributes = {key: item.get(key, '') for key in item if key != 'api_results'}
        api_results = item.get('api_results', [])

        logMsg(f"Processing data source: {dataSource} for item: {topLevelAttributes}")
        if dataSource == "flickr":
            # Insert top-level attributes into the main data table
            print(f'\n\ntopLevelAttributes1: {topLevelAttributes}\n\n')
            subjGen_insertData(conn, topLevelAttributes, load_id, load_date, load_job, dataSource)

            #Process each URL in api_results
            for url in api_results:
                # Create a separate data entry for each URL
                url_data = {
                    "resultID": topLevelAttributes["insightID"],
                    "searchID": topLevelAttributes["searchID"],
                    "resultID": topLevelAttributes["resultID"],
                    "category": topLevelAttributes["category"],
                    "img_url": url
                }
                print(f'url_data: \n\n{url_data}\n\n')
                # Insert each URL into the URL-specific table   
                subjGen_insertData(conn, url_data, load_id, load_date, load_job, "flickr_url")
        elif dataSource == "youtube" or dataSource == "yt":
            # For other data sources, flatten and process as before
            for api_result in api_results:
                flattened_item = {**topLevelAttributes, **api_result}
                print(f'flattened_item {flattened_item} of type: {type(flattened_item)}')
                subjGen_insertData(conn, flattened_item, load_id, load_date, load_job, dataSource)
        elif dataSource == "wiki":
            # Process each URL in api_results
            for api_result in api_results:

                wiki_data = {
                "searchID": topLevelAttributes["searchID"],
                "wiki_result_id": api_result["wiki_result_id"],
                "resultID": topLevelAttributes["resultID"],
                "insightID": topLevelAttributes["insightID"],
                "category": topLevelAttributes["category"],
                "dataSource": topLevelAttributes["dataSource"],
                "searchTerm": topLevelAttributes["searchTerm"],
                "extractData": api_result["extract"],
                "subjTitle":api_result["subjTitle"],
                "pageURL":api_result["pageURL"],
                "utcTime": api_result["utcTime"]
                }
                subjGen_insertData(conn, wiki_data, load_id, load_date, load_job, dataSource)
                
                # Iterate over each URL in the 'images' list of the current api_result
                i=0
                for url in api_result['images']:
                    # Create a separate data entry for each URL
                    url_data = {
                        "searchID": topLevelAttributes["searchID"],
                        "wiki_result_id": api_result["wiki_result_id"],
                        "resultID": topLevelAttributes["resultID"],
                        "insightID": topLevelAttributes["insightID"],
                        "img_url": url  # Use the individual URL here
                    }
                    # Insert each URL into the URL-specific table
                    subjGen_insertData(conn, url_data, load_id, load_date, load_job, "wiki_url")
            
    cursor.commit()
    closeDB(cursor, conn)

def loadDB(directory, pattern):
    # Ensure pattern includes wildcard characters if needed
    wildcard_pattern = f'*{pattern}*' if '*' not in pattern else pattern
    #print(f'Searching in directory: {directory} for pattern: {wildcard_pattern}')
    processed_files = []  # List to keep track of processed files

    aggregated_data = {}
    for file_path in glob.glob(os.path.join(directory, wildcard_pattern)):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                for item in data:
                    dataSource = item.get('dataSource', '').lower()
                    if dataSource not in aggregated_data:
                        aggregated_data[dataSource] = []
                    aggregated_data[dataSource].append(item)
            #print(f"Successfully processed file: {file_path}")
            processed_files.append(file_path)  # Add file to the list of processed files
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    for dataSource, items in aggregated_data.items():
        loadSubjGenData(dataSource, items)

    # Archive processed files if there are any
    if processed_files:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_file = f'{archive_name}_{timestamp}.zip'
        archive_file = os.path.join(directory, archive_dir, archive_file)
        #archiveData(processed_files, archive_file)

if __name__ == "__main__":
    logMsg(f"starting main in {program_name}")
    parser = argparse.ArgumentParser(description="Load JSON data into PostgreSQL database.")
    parser.add_argument("directory", help="Directory containing JSON files")
    parser.add_argument("pattern", help="Pattern to match JSON files")
    args = parser.parse_args()
    logMsg(f"starting with args: {args}")
    directory = args.directory
    pattern = args.pattern
    loadDB(directory, pattern)
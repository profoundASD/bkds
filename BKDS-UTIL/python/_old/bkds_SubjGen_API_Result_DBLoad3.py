import json
import os
import glob
import argparse
from datetime import datetime
import argparse
import time
#custom functions
from bkdsUtilities import log_msg, getHash, get_sqlTemplate, getDBConn, closeDB, getHash, archiveData

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id=f'SUBJ_GEN_MAIN'

src_key='dataSource'
api_key='api_results'
templateKey = 'subjGen_insertData'

#for archiving processed data
proc_prefix='bkds_SubjGen'
archive_dir='archive'

mapping_file='bkds_data_mappings.json'
mapping_env=os.getenv('BKDS_UTIL')
mapping_dir=os.path.join(mapping_env, 'sql', mapping_file)
########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getInsert(dataSource):  
    return get_sqlTemplate(f"subjGen_insertData_{dataSource}")

def load_column_mappings(mapping_path, mapping_key):
    with open(mapping_path, 'r') as file:
        data = json.load(file)
        # Retrieve the specific mapping using the provided key
        mapping = data['column_mappings'].get(mapping_key)
        if mapping:
            return mapping['columns']
        else:
            raise ValueError(f"No mapping found for key: {mapping_key}")

def insertData(cursor, data, load_id, load_date, load_job, dataSource):
    logMsg(f"Inserting data for {dataSource} with load_id {load_id}")
    proc_prefix = "bkds_subjGen"  # assuming proc_prefix is defined elsewhere
    mapping_key = f'{proc_prefix}_{dataSource}'
    columns = load_column_mappings(mapping_dir, mapping_key)
    #columns = column_mapping[dataSource]
    record_id = getHash(json.dumps(data))  
    
    json_values = tuple(data.get(key, '') for key in columns)
    data_values = (record_id,) + json_values + (load_id, load_date, load_job)

    sql_query = getInsert(dataSource)
    if sql_query and data_values:
        cursor.execute(sql_query, data_values)

def mergeData(topLevelAttributes, api_result=None, additional_fields=None):
    data = topLevelAttributes.copy()
    if api_result:
        data.update(api_result)
    if additional_fields:
        data.update(additional_fields)
    return data


def generateFlickrInsertStatements(json_data):
    print(f"Data type: {type(json_data)}")
    data_to_insert = []

    searchID = json_data.get("searchID", "")
    resultID = json_data.get("resultID", "")
    insightID = json_data.get("insightID", "")
    category = json_data.get("category", "")
    searchTerm = json_data.get("searchTerm", "")
    utcTime = json_data.get("utcTime", "")

    for api_result in json_data.get("api_results", []):
            # Append data as a tuple
            resultID=getHash(api_result+resultID)
            data_to_insert.append((searchID, resultID, insightID, category, searchTerm, api_result, utcTime))


    # Connect to the database and execute the insert statements
    conn, cursor = getDBConn()
    insert_query = "INSERT INTO dev.stg_flickr_api_results (searchID, resultID, insightID, category, searchTerm, imageUrl, utcTime) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    print(insert_query)
    print(data_to_insert)

    conn.executemany(insert_query, data_to_insert)
    
    cursor.commit()
    #time.sleep(30)
    closeDB(cursor, conn)

    return data_to_insert  # Returns the data that was inserted

def generateWikiInsertStatements(json_data):
    print(f"Data type: {type(json_data)}")
    data_to_insert = []

    searchID = json_data.get("searchID", "")
    resultID = json_data.get("resultID", "")
    insightID = json_data.get("insightID", "")
    category = json_data.get("category", "")
    searchTerm = json_data.get("searchTerm", "")
    utcTime = json_data.get("utcTime", "")

    for api_result in json_data.get("api_results", []):
        wiki_result_id = api_result.get("wiki_result_id", "")
        subjTitle = api_result.get("subjTitle", "")
        pageURL = api_result.get("pageURL", "")
        extract = api_result.get("extract", "")
        resultID=getHash(pageURL+resultID)
        for image_url in api_result.get("images", []):
            # Append data as a tuple
            data_to_insert.append((searchID, resultID, insightID, category, searchTerm, wiki_result_id, subjTitle, pageURL, extract, image_url, utcTime))

    # Connect to the database and execute the insert statements
    conn, cursor = getDBConn()
    insert_query = "INSERT INTO dev.stg_wiki_api_results (searchID, resultID, insightID, category, searchTerm, wiki_result_id, subjTitle, pageURL, extract, imageUrl, utcTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    print(insert_query)
    print(data_to_insert)

    conn.executemany(insert_query, data_to_insert)
    
    cursor.commit()
    closeDB(cursor, conn)

    return data_to_insert  # Returns the data that was inserted

def generateYoutubeInsertStatements(json_data):
    print(f"Data type: {type(json_data)}")
    data_to_insert = []

    searchID = json_data.get("searchID", "")
    resultID = json_data.get("resultID", "")
    insightID = json_data.get("insightID", "")
    category = json_data.get("category", "")
    searchTerm = json_data.get("searchTerm", "")
    utcTime = json_data.get("utcTime", "")

    for api_result in json_data.get("api_results", []):
        title = api_result.get("title", "")
        description = api_result.get("description", "")
        thumbnail = api_result.get("thumbnail", "")
        url = api_result.get("url", "")
        timestamp = api_result.get("timestamp", "")
        resultID=getHash(url+resultID)
        # Append data as a tuple
        data_to_insert.append((searchID, resultID, insightID, category, searchTerm, title, description, thumbnail, url, timestamp, utcTime))

    # Connect to the database and execute the insert statements
    conn, cursor = getDBConn()
    insert_query = "INSERT INTO dev.stg_youtube_api_results (searchID, resultID, insightID, category, searchTerm, title, description, thumbnail, videoUrl, timestamp, utcTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    print(insert_query)
    print(data_to_insert)

    conn.executemany(insert_query, data_to_insert)
    
    cursor.commit()
    closeDB(cursor, conn)

    return data_to_insert  # Returns the data that was inserted

def loadSubjGenData(dataSource, items):
    logMsg(f"Loading data for dataSource: {dataSource}")
    load_date = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    load_id = getHash(load_date)
    load_job = 'loadSubjGenData'

    conn, cursor = getDBConn()
    
    for item in items:
        topLevelAttributes = {key: item.get(key, '') for key in item if key != 'api_results'}
        api_results = item.get('api_results', [])

        # Insert top-level attributes only once per item
     #   insertData(conn, topLevelAttributes, load_id, load_date, load_job, dataSource)

        # Process API results
      #  processApiResults(conn, dataSource, topLevelAttributes, api_results, load_id, load_date, load_job)
                
    cursor.commit()
    closeDB(cursor, conn)

def processApiResults(conn, dataSource, topLevelAttributes, api_results, load_id, load_date, load_job):
    if dataSource == "flickr":
        for url in api_results:
            insert_data = mergeData(topLevelAttributes, additional_fields={"img_url": url})
            insertData(conn, insert_data, load_id, load_date, load_job, "flickr_url")
    elif dataSource == "wiki":
        for api_result in api_results:
            insert_data = mergeData(topLevelAttributes, api_result)
            insertData(conn, insert_data, load_id, load_date, load_job, dataSource)
            for url in api_result.get('images', []):
                insert_data = mergeData(topLevelAttributes, additional_fields={"wiki_result_id": api_result["wiki_result_id"], "img_url": url})
                insertData(conn, insert_data, load_id, load_date, load_job, "wiki_url")

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
                    if item.get("dataSource", "").lower() == "wiki":
                        generateWikiInsertStatements(item)
                    elif item.get("dataSource", "").lower() == "flickr":
                        generateFlickrInsertStatements(item)
                    elif item.get("dataSource", "").lower() == "youtube":
                        generateYoutubeInsertStatements(item)                        
                #time.sleep(20)

            #print(f"Successfully processed file: {file_path}")
            processed_files.append(file_path)  # Add file to the list of processed files
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
   # print('aggregated_data.items()', aggregated_data.items())
    i=0
    for dataSource, items in aggregated_data.items():
        i=i+1
        print(f'looping {i}')
        #generateFlickrInsertStatements(aggregated_data.items())
   #     loadSubjGenData(dataSource, items)

    # Archive processed files if there are any
    if processed_files:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_file = f'{proc_prefix}_{timestamp}.zip'
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
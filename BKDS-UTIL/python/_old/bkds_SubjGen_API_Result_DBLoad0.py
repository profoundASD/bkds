import json
import os
import glob
import argparse
from datetime import datetime
import argparse
import zipfile
#custom functions
from bkdsUtilities import log_msg, getFunctionName, getHash, get_sqlTemplate, getDBConn, closeDB, getHash

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
batch_id=f'SUBJ_GEN__MAIN'



src_key='dataSource'
api_key='api_results'
templateKey = 'subjGen_insertData'

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def getInsert(dataSource):

    if dataSource == "youtube" or dataSource == "yt":
        sql_query = f"""INSERT INTO dev.stg_api_youtube_data (
        record_id, title, description, thumbnail_url, video_url, utc_timestamp,
        search_id, result_id, insight_id, category, data_source,
        search_term, load_id, load_date, load_job
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return sql_query
    elif dataSource == "flickr":
        sql_query_data = f"""INSERT INTO dev.stg_api_flickr_data(
            record_id, search_id, result_id, insight_id, category, 
            data_source, search_term, utc_timestamp, load_id, load_date, load_job
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return sql_query_data
    elif dataSource == "flickr_url":
        # SQL query for inserting into dev.stg_api_flickr_data_urls
        sql_query_urls = f"""INSERT INTO dev.stg_api_flickr_data_urls (
                record_id, result_id, url, load_id, load_date, load_job
            ) VALUES (%s, %s, %s, %s, %s, %s)"""
        return sql_query_urls
    elif dataSource == "wiki":
        sql_query_data = f"""INSERT INTO dev.stg_api_wiki_data(
            record_id, search_id, wiki_result_id, result_id,  insight_id, category, 
            data_source, search_term, extract_data, page_title, page_url, utc_timestamp,
            load_id, load_date, load_job
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return sql_query_data
    elif dataSource == "wiki_url":
        sql_query_urls = f"""INSERT INTO dev.stg_api_wiki_data_urls (
            record_id, search_id, wiki_result_id, result_id, insight_id, img_url, load_id, load_date, load_job
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return sql_query_urls

def subjGen_insertData(cursor, json_data, load_id, load_date, load_job, dataSource):
    logMsg(f"starting subjGen_insertData with {load_id} for {dataSource}")

    record_id = getHash(json.dumps(json_data))  # Unique identifier
    data_values=None

    if dataSource == "flickr":
        # Prepare data for flickr_data table
        data_values = (record_id, json_data['searchID'], json_data['resultID'],
                    json_data['insightID'], json_data['category'],
                    dataSource, json_data['searchTerm'], json_data['utcTime'],
                    load_id, load_date, load_job)

        sql_query = getInsert(dataSource)
        cursor.execute(sql_query, data_values)

        # Insert each URL into flickr_urls table
        #print(f'json_data\n{json_data}')  
    elif dataSource == "flickr_url":
        #print(f'json_data\n{json_data}')
        record_id = getHash(json.dumps(json_data))  # Generate a unique record_id
        data_values = (record_id, json_data['resultID'], json_data['url'], load_id, load_date, load_job)

    elif dataSource == "youtube":
        data_values = (record_id, json_data['searchID'], json_data['resultID'],
                json_data['insightID'], json_data['category'],
                dataSource, json_data['searchTerm'], json_data['utcTime'],
                load_id, load_date, load_job)
        
        # Handle other data sources (YouTube, etc.)
        columns_order = ['title', 'description', 'thumbnail', 'url', 
                         'utcTime', 'searchID', 'resultID', 'insightID', 'category', 
                         'dataSource', 'searchTerm']

        json_values = tuple(json_data.get(key, '') for key in columns_order)
        data_values = (record_id,) + json_values + (load_id, load_date, load_job)
    elif dataSource == "wiki":  
        # Insert data into the main wiki data table  
        #print(f'\njson_data wiki: {json_data}')
        import time
        #time.sleep(25)
        data_values = (record_id, json_data['searchID'], json_data['wiki_result_id'], json_data['resultID'],
                    json_data['insightID'], json_data['category'], dataSource, json_data['searchTerm'],
                    json_data['extractData'], json_data['subjTitle'], json_data['pageURL'], json_data['utcTime'],
                    load_id, load_date, load_job)


    elif dataSource == "wiki_url":
        #print(f'json_data\n{json_data}')
        record_id = getHash(json.dumps(json_data))  # Generate a unique record_id
        data_values = (record_id, json_data['searchID'], json_data['wiki_result_id'], json_data['resultID'],
                    json_data['insightID'], json_data['img_url'], 
                       load_id, load_date, load_job)

    sql_query = getInsert(dataSource)
    print(f'sql_query\n\n{sql_query}')
   # print(f'data_values\n\n{data_values}')
    if sql_query:
        cursor.execute(sql_query, data_values)

def loadSubjGenData(dataSource, items):
    logMsg(f"starting loadSubjGenData for dataSource: {dataSource}")
    load_date = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    load_id = getHash(load_date)
    load_job = 'loadSubjGenData'

    conn, cursor = getDBConn()
    #print(f'showing items \n{items}')

    for item in items:
        # Extract top-level attributes
        topLevelAttributes = {key: item.get(key, '') for key in item if key != 'api_results'}
        api_results = item.get('api_results', [])

       # logMsg(f"Processing data source: {dataSource} for item: {topLevelAttributes}")
   
        if dataSource == "flickr":
            # Insert top-level attributes into the main data table
            subjGen_insertData(conn, topLevelAttributes, load_id, load_date, load_job, dataSource)

            # Process each URL in api_results
            for url in api_results:
                # Create a separate data entry for each URL
                url_data = {
                    "resultID": topLevelAttributes["insightID"],
                    "searchID": topLevelAttributes["searchID"],
                    "resultID": topLevelAttributes["resultID"],
                    "category": topLevelAttributes["category"],
                    "url": url
                }
                # Insert each URL into the URL-specific table
                subjGen_insertData(conn, url_data, load_id, load_date, load_job, "flickr_url")
        elif dataSource == "youtube" or dataSource == "yt":
            # For other data sources, flatten and process as before
            for api_result in api_results:
                flattened_item = {**topLevelAttributes, **api_result}
                subjGen_insertData(conn, flattened_item, load_id, load_date, load_job, dataSource)
        elif dataSource == "wiki":
            # Insert top-level attributes into the main data table
            #print(f'api_results1\n\n{api_results}')
            import time
            #time.sleep(40)
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
                #print(f'api_result:\n{api_result}\n\n')
                
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
                    #time.sleep(3)
            
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
    print('aggregated_data.items()')
    print(aggregated_data.items())
    for dataSource, items in aggregated_data.items():
        loadSubjGenData(dataSource, items)

    # Archive processed files if there are any
    if processed_files:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_name = f'archive_{timestamp}.zip'
        archive_path = os.path.join(directory, 'archive', archive_name)

        # Create archive directory if it doesn't exist
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)

        # Create a zip file and add processed files
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for file in processed_files:
                zipf.write(file, os.path.basename(file))
                os.remove(file)  # Optionally remove the file after archiving

        print(f'Processed files are archived in {archive_path}')


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
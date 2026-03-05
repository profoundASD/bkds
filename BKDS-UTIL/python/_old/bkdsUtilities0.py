"""
Utility Module for Subject Insights Generation

This module contains utility functions to support the generation of insights for various subjects, 
including Flickr image search, logging, and file handling. It offers a suite of tools to streamline 
the insight generation process across different data sources.

Functions:
- log_msg(program_name, batch_id, message): Logs messages with program name and batch ID.
- logMsg(msg): Wrapper function for logging messages with predefined settings.
- subjGenOutputHandler(data, subjType, output_prefix, output_type, keyword, subjID, timestamp): Saves processed data to JSON files.
- genInsightID(search_term, string_id, category): Generates unique hashes for insight identification.
- getFlickrData(keyword, num_images, api_key): Fetches image URLs from Flickr based on a given keyword.
- isValidImage(image_url, image_title): Validates if a given image URL meets specific criteria.

Environment Variables:
- BKDS_NODEJS_SUBJGEN: Output directory for generated insights.
- BKDS_LOGS: Directory for logging messages.

Notes:
- The module ensures efficient handling and logging of data across different components of the subject insights generation pipeline.
- It abstracts complex functionalities into simpler, reusable functions to enhance maintainability and scalability.
"""
import hashlib
import glob
import os
import sys
import logging
import socket
import json
import re
from datetime import datetime 
import psycopg2
import psycopg2.extras
import uuid
import inspect
from collections import OrderedDict
import zipfile
import time
#####################################################################
# Main Setup / Variables

output_dir=os.getenv('BKDS_NODEJS_SUBJGEN')

# Database Connection Parameters
conn_params = {
    "host": "localhost",
    "database": "bkds",
    "user": "bkdsdev",
    "password": "hello"
}
program_name=os.path.basename(sys.argv[0])
########################################################################
#  Main logic and functions
def logMsg(msg):
    log_msg(program_name, f'BKDS_UTIL_LOGMSG', msg)
    print(msg)

def getDBConn(cursor_type=None):
    """
    Returns a cursor to the database. If 'dict' is specified as the cursor_type,
    returns a dictionary cursor.

    Parameters:
    cursor_type (str, optional): Type of the cursor. If 'dict', returns a DictCursor.

    Returns:
    psycopg2.cursor: A cursor to the database.
    """
      # Replace with your actual connection parameters
    conn = psycopg2.connect(**conn_params)
    if cursor_type == 'dict':
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor), conn
    else:
        return conn.cursor(), conn

def closeDB(cursor, conn):
    cursor.close()
    conn.close()

def fetch_data(query):
    logMsg(f'fetchData with {query}')
    try:
        # Assuming conn_params is defined somewhere in your code
        cursor, conn = getDBConn('dict')
        cursor.execute(query)
        result = cursor.fetchall()
        result = [dict(row) for row in result]
        closeDB(cursor, conn)
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database Error: {error}")
        return None

def structure_data_as_json(data):
    """
    Convert database query results into a list of dictionaries.
    Each dictionary represents a row, with keys as column names.

    :param data: Query result data, assumed to be a list of tuples.
    :return: List of dictionaries representing the structured data.
    """
    structured_data = []
    columns = ["insightid", "keyword", "category", "subject"]

    for row in data:
        row_dict = dict(zip(columns, row))
        structured_data.append(row_dict)

    return structured_data


log_path = os.getenv("BKDS_LOGS")
if not log_path:
    raise ValueError("BKDS_LOGS environment variable is not set.")

loggers = {}

def log_msg(program_name, batch_id, message):
    """
    Log a message with the specified program name and batch ID.
    :param program_name: The name of the program.
    :param batch_id: The batch identifier.
    :param message: The message to log.
    """
    logger_key = f"{program_name}_{batch_id}"
    hostname = socket.gethostname()
    logger = logging.getLogger(f"{hostname}_{batch_id}_{program_name}")

    log_directory = os.path.join(log_path, hostname, datetime.utcnow().strftime('%Y%m%d'), batch_id)
    os.makedirs(log_directory, exist_ok=True)
    log_file_name = f"{hostname}_{batch_id}_{program_name}_{datetime.utcnow().strftime('%Y%m%d%H')}.log"
    log_file = os.path.join(log_directory, log_file_name)    

    if logger_key not in loggers:
        if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.baseFilename == log_file):
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False
            loggers[logger_key] = logger

    try:
        logger.info(message)
        for handler in logger.handlers:
            handler.flush()
    except Exception as e:
        print(f"Error while logging: {e}")

def getHash(data):
    enriched_contents_str = json.dumps(data, indent=4)
    hash_object = hashlib.md5(enriched_contents_str.encode())
    return hash_object.hexdigest()

def getFunctionName():
    return inspect.currentframe().f_code.co_name

def subjGenOutputHandler(data, subjType, output_prefix, output_type, keyword, subjID):
    """
    Saves the processed data to a JSON file.
    
    :param output_dir: Output directory.
    :param data: Data to be saved.
    :param subjType: Subject type.
    :param output_prefix: Prefix for the output filename.
    :param output_type: Type of the output file.
    :param keyword: The keyword used for searching.
    :param subjID: Subject ID.
    :param timestamp: Timestamp for the filename.
    :return: The path of the saved file.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    keyword_cleaned = re.sub(r'[^a-zA-Z0-9_]+', '_', keyword).strip('_')
    output_filepath = os.path.join(output_dir, f'{subjType}/{output_prefix}_{subjType}_{keyword_cleaned}_{subjID}_{timestamp}.{output_type}')
    output_filepath = output_filepath.replace('__', '_')
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    logMsg(f'output_filepath {output_filepath}')
    with open(output_filepath, 'w') as output_file:
        json.dump(data, output_file, indent=4)

    return output_filepath


def genInsightID(search_term, string_id, category):
    """
    Generate a unique hash based on the concatenation of the search term, URL, and category.
    :param search_term: The search term used.
    :param string_id: A string identifier.
    :param category: The category of the item.
    :return: A unique hash.
    """
    logMsg(f"generate_insight_id: {search_term}")
    combined_string = f"{search_term}{string_id}{category}".encode('utf-8')[:100]
    return hashlib.sha256(combined_string).hexdigest()  


def isValidImage(image_url, image_title):
    """
    Checks if an image URL corresponds to a valid image based on certain criteria.
    """
    if image_url is None:
        return False

    upper_url = image_url.upper()
    upper_title = image_title.upper()
    invalid_keywords = [
        "PROTECTED", "PROTECTION", "PENDING", "FEATURED",
        "LISTEN", "SYMBOL", "QUESTION_BOOK", "WIKI_LETTER",
        "TEXT_DOCUMENT", "QUESTION_MARK", "EMBLEM-MONEY", "ICON",
        "RED_PENCIL"  # Add or remove keywords as needed
    ]

    # Filter based on file type and URL contents
    if (upper_title.endswith(('.PNG', '.JPG', '.JPEG', '.GIF')) and
        all(keyword not in upper_url for keyword in invalid_keywords)):
        return True

    return False


def infer_data_type(value):
    """Infer the SQL data type from a Python data type."""
    if isinstance(value, int):
        return 'TEXT'
    elif isinstance(value, float):
        return 'TEXT'
    elif isinstance(value, bool):
        return 'TEXT'
    else:
        # Default fallback type
        return 'TEXT'


def flatten_json(data):
    """Flattens a nested JSON object."""
    flat_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_data[f"{key}_{sub_key}"] = sub_value
        else:
            flat_data[key] = value
    return flat_data


def db_load_llm_chat(file_name, target_table):
    # Read data from file
    with open(file_name, 'r') as file:
        data_list = json.load(file)

    # Filter data for "assistant" role
    assistant_data = [item for item in data_list if item.get('role') == 'assistant']

    cursor, conn = getDBConn()

    # Gather all unique keys from assistant_data using OrderedDict to preserve order
    all_keys = OrderedDict()
    for data in assistant_data:
        flat_data = flatten_json(data)
        for key in flat_data:
            if key not in all_keys:
                all_keys[key] = infer_data_type(flat_data[key])

    # Dynamically create column definitions based on all possible keys
    column_definitions = ', '.join([f"{key} {all_keys[key]}" for key in all_keys])
    column_definitions += ', load_id VARCHAR(255), load_date TIMESTAMP, load_process VARCHAR(255)'

    # SQL for creating table if it doesn't exist
    create_table_query = f"CREATE TABLE IF NOT EXISTS {target_table} ({column_definitions});"
    cursor.execute(create_table_query)

    # Process each item for insertion
    for data in assistant_data:
        # Flatten the JSON data
        flat_data = flatten_json(data)

        # Prepare insert query
        insert_columns = ', '.join(all_keys.keys()) + ', load_id, load_date, load_process'
        placeholders = ', '.join(['%s'] * len(all_keys)) + ', %s, %s, %s'
        insert_query = f"INSERT INTO {target_table} ({insert_columns}) VALUES ({placeholders});"

        load_id = str(uuid.uuid4())
        load_date = datetime.utcnow()
        load_process = program_name  # Replace with your process name
        insert_data = tuple(flat_data.get(key, None) for key in all_keys) + (load_id, load_date, load_process)

        # Execute insert query
        cursor.execute(insert_query, insert_data)

    # Commit the transaction
    conn.commit()
    # Close cursor and connection
    closeDB(cursor, conn)


def get_sqlTemplate(query_key, target_table=None):
    logMsg(f"starting get_sqlTemplate")
    file_path = os.path.join(os.path.dirname(__file__), '../sql/bkds_subjGenQueryTemplates.json')
    cursor, conn = getDBConn()

    with open(file_path, 'r') as file:
        query_templates = json.load(file)

    # Find the query template based on the query_key
    for template in query_templates:
        logMsg(f"checking {query_key} template['query_id'] {template['query_id']}")
        if template['query_id'] == query_key:
            logMsg(f"found {query_key} template['query_id']")
            src_schema = template['src_schema']
            src_data = template['src_data']
            columns_formatted=None
            values_placeholder=None
            clause_formatted=None
            # Modify the SQL query template
            sql_query = template['sql_query']
            print(template)
         
            if 'insert' in sql_query.lower():
                if template['src_columns']:
                    src_column_names=template['src_columns']

                    src_column_names = src_column_names.split(", ")  # Adjust the delimiter if necessary


                    columns_formatted = ', '.join(src_column_names)
                    print(f'columns_formatted {columns_formatted} {type(columns_formatted)}')
                else:
                    column_names = get_column_names(f'{src_schema}.{src_data}', cursor)
                    # Retrieve column names for the table
                    columns_formatted = ', '.join(column_names)
                    logMsg(f"values_placeholder {values_placeholder}")

                print(f'src_column_names3\n {src_column_names}\n src_column_names[0]]: {src_column_names[0]}')
                values_placeholder = ', '.join(['%s' for _ in columns_formatted.split(',')])

            if template['clause']:
                clause_placeholder = template['clause']
                # Format the clause with target_table if provided
                if target_table:
                    clause_formatted = clause_placeholder.format(src_schema=src_schema, src_obj=target_table)
                else:
                    clause_formatted = clause_placeholder.format(src_schema=src_schema)
                    
            logMsg(f"\npre src_schema for {src_schema}")
            logMsg(f"\npre src_data for {src_data}")
            logMsg(f"\npre values_placeholder for {values_placeholder}")
            logMsg(f"\npre columns_formatted for {columns_formatted}")

            print(f"src_schema: {src_schema}, src_data: {src_data}, src_columns: {columns_formatted}, values: {values_placeholder}, clause: {clause_formatted}")
            print(f'sql_query\n {sql_query}')
            table_name = f"{src_schema}.{src_data}" 
            formatted_query = sql_query.format(src_schema=src_schema, 
                                               table_name=table_name, 
                                               src_columns=columns_formatted, 
                                               values=values_placeholder, 
                                               clause=clause_formatted)
            
            logMsg(f"\n\post formatted_query for {formatted_query}")
            closeDB(cursor, conn)
            return formatted_query
        else:
            pass
        
    closeDB(cursor, conn)
    return None

def get_column_names(target_table, cursor):
    # Replace the query below with the one suitable for your database system
    templateKey='select_query_get_column_names'

    sql_query=get_sqlTemplate(templateKey, target_table)
    
    cursor.execute(sql_query)
    columnList=[row[0] for row in cursor.fetchall()]

    return columnList

def archiveData(processed_files, archive_path):
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)

    # Create a zip file and add processed files
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
            os.remove(file)  # Optionally remove the file after archiving

    print(f'Processed files are archived in {archive_path}')
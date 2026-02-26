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
from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
import uuid
import inspect
from collections import OrderedDict
import zipfile
import time
#####################################################################
# Main Setup / Variables

#output_dir=os.getenv('BKDS_NODEJS_SUBJGEN')

# Database Connection Parameters
conn_params = {
    "host": "localhost",
    "database": "bkds_prod",
    "user": "bkdsdev",
    "password": "hello"
}
program_name=os.path.basename(sys.argv[0])

bkds_util_env = os.getenv('BKDS_UTIL')
bkds_util_data = os.getenv('BKDS_UTIL_DATA')

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
    logMsg(f'fetchData with query: {query}')
    try:
        # Assuming conn_params is defined somewhere in your code
        cursor, conn = getDBConn('dict')
        
        # Log database connection details
        db_details = conn.get_dsn_parameters()  # Get details about the connection
        print(f"Connected to DB with details: {db_details}")

        # Execute query
        cursor.execute(query)
        result = cursor.fetchall()
        result = [dict(row) for row in result]
        
        closeDB(cursor, conn)
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database Error: {error}")
        return None


def load_and_resolve_config(config_key, config_path=None, config_json=None):
    """
    Load a configuration file or JSON string and resolve $ref keys.

    Parameters:
        config_key (str): The key to extract the specific configuration.
        config_path (str): Path to the JSON configuration file (optional).
        config_json (str): JSON string of the configuration (optional).

    Returns:
        dict: The resolved configuration for the given key.

    Raises:
        ValueError: If neither config_path nor config_json is provided.
        FileNotFoundError: If the configuration file is not found.
        KeyError: If the config_key is not found or $ref cannot be resolved.
        json.JSONDecodeError: If the JSON data cannot be parsed.
    """
    def resolve_refs(config, root_config=None):
        """Recursively resolve $ref keys in the JSON configuration."""
        if root_config is None:
            root_config = config  # Set root config on the first call

        if not isinstance(config, dict):
            return config
        
        resolved_config = {}
        for key, value in config.items():
            if key == "$ref" and isinstance(value, str):
                # Handle $ref: Copy values from the referenced key
                if value not in root_config:
                    raise KeyError(f"Referenced key '{value}' not found in root configuration.")
                ref_data = root_config[value]
                resolved_config.update(resolve_refs(ref_data, root_config))
            elif isinstance(value, dict):
                resolved_config[key] = resolve_refs(value, root_config)
            else:
                resolved_config[key] = value
        
        return resolved_config

    # Load the configuration data
    if config_path:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        with open(config_path, 'r') as cfg_file:
            config_data = json.load(cfg_file)
    elif config_json:
        config_data = json.loads(config_json)
    else:
        raise ValueError("Either 'config_path' or 'config_json' must be provided.")

    # Resolve $ref references
    resolved_config = resolve_refs(config_data)

    # Return the specific configuration key
    if config_key not in resolved_config:
        raise KeyError(f"Configuration key '{config_key}' not found in configuration.")
    
    return resolved_config[config_key]

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
    try:
        # Attempt to serialize data to JSON
        enriched_contents_str = json.dumps(data, indent=4)
    except TypeError:
        # Handle the case where data is not serializable
        enriched_contents_str = json.dumps(str(data), indent=4)
    except Exception as e:
        # General error handling, optionally log the error
        logMsg(f"Error in getHash with data {data}: {e}")
        return None  # Or handle differently as needed

    hash_object = hashlib.md5(enriched_contents_str.encode())
    return hash_object.hexdigest()

def getFunctionName():
    return inspect.currentframe().f_code.co_name

def subjGenOutputHandler(data, subjType, output_prefix, output_type, keyword, subjID, env_dir=None):
    """
    Saves the processed data to a JSON file.
    
    :param data: Data to be saved.
    :param subjType: Subject type.
    :param output_prefix: Prefix for the output filename.
    :param output_type: Type of the output file.
    :param keyword: The keyword used for searching.
    :param subjID: Subject ID.
    :param output_dir: Optional; if provided, overrides the default output directory.
    :return: The path of the saved file.
    """
    # If output_dir is not provided, use the global output_dir
    if env_dir:
        output_dir = env_dir  # This assumes a global 'output_dir' variable is defined elsewhere
    else:
        output_dir=os.getenv('BKDS_UTIL_DATA')

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    keyword_cleaned = re.sub(r'[^a-zA-Z0-9_]+', '_', keyword).strip('_')
    output_filepath = os.path.join(output_dir, subjType, 'output', output_type, 
                                   f'{output_prefix}_{subjType}_{keyword_cleaned}_{subjID}_{timestamp}.{output_type}')
    output_filepath = output_filepath.replace('__', '_')
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    logMsg(f'output_filepath {output_filepath}')
    
    with open(output_filepath, 'w') as output_file:
        json.dump(data, output_file, indent=4)

    return output_filepath


def genInsightID(text_data, string_id, category):
    """
    Generate a unique hash based on the concatenation of the search term, URL, and category.
    :param text_data: The search term used.
    :param string_id: A string identifier.
    :param category: The category of the item.
    :return: A unique hash.
    """
    logMsg(f"generate_insight_id with : {text_data}")
    combined_string = f"{text_data}{string_id}{category}".encode('utf-8')[:100]
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
        load_date = datetime.now(timezone.utc)
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
    #file_path = os.path.join(os.path.dirname(__file__), '../sql/bkds_data_mappings.json')
    file_path = os.path.join(bkds_util_data, 'config', 'bkds_data_mappings.json')

    cursor, conn = getDBConn()

    with open(file_path, 'r') as file:
        data = json.load(file)
        query_templates = data[0]

        template = query_templates[query_key]
        logMsg(f"found template for {query_key}")
        # Find the query template based on the query_key
        for template in query_templates:
            logMsg(f"checking {query_key} template['query_id'] {template}")
            if query_key in query_templates:
                template = query_templates[query_key]
                logMsg(f"found template for {query_key}")
                
                # Process the template as needed
                src_schema = template.get('src_schema', 'default_schema')
                src_data = template.get('src_data', 'default_data')
                src_column_names = template.get('src_columns', 'default_column_names')
                src_clause = template.get('clause', 'default_clause')

                columns_formatted = None
                values_placeholder = None
                clause_formatted = src_clause
                # Modify the SQL query template
                sql_query = template['sql_query']
                
                #print(f"template[src_columns] {template}")
                if template['src_columns']:
                    #print(f'src_column_names {src_column_names}')
                    src_column_names = src_column_names.split(", ")  # Adjust the delimiter if necessary
                    print(f'src_column_names {src_column_names}')
                # print(src_column_names.split(", "))

                    columns_formatted = ', '.join(src_column_names)
                    print(columns_formatted)

                else:
                    column_names = get_column_names(f'{src_schema}.{src_data}', cursor)
                    # Retrieve column names for the table
                    columns_formatted = ', '.join(column_names)

                    values_placeholder = ', '.join(['%s' for _ in columns_formatted.split(',')])

                if template['clause']:
                    clause_placeholder = template['clause']
                    # Format the clause with target_table if provided
                    if target_table:
                        clause_formatted = clause_placeholder.format(src_schema=src_schema, src_obj=target_table)
                    else:
                        clause_formatted = clause_placeholder.format(src_clause=src_clause)
                        
                print(f"\npre src_schema for {src_schema}")
                print(f"\npre src_data for {src_data}")
                print(f"\npre values_placeholder for {values_placeholder}")
                print(f"\npre columns_formatted for {columns_formatted}")

                print(f"src_schema: {src_schema}, src_data: {src_data}, src_columns: {columns_formatted}, values: {values_placeholder}, clause: {clause_formatted}")
                print(f'sql_query\n {sql_query}')
                
                table_name = f"{src_schema}.{src_data}" 
                formatted_query = sql_query.format(src_schema=src_schema, 
                                                src_data=src_data, 
                                                src_columns=columns_formatted, 
                                                values=values_placeholder, 
                                                clause=clause_formatted)
                
                print(f"\nformatted_query for {formatted_query}")
                
                closeDB(cursor, conn)
                return formatted_query
            else:
                raise ValueError(f"No template found for key: {query_key}")   
    
    closeDB(cursor, conn)
    return None

def get_column_names(target_table, cursor):
    # Replace the query below with the one suitable for your database system
    templateKey='select_query_get_column_names'

    sql_query=get_sqlTemplate(templateKey, target_table)
    
    cursor.execute(sql_query)
    columnList=[row[0] for row in cursor.fetchall()]

    return columnList

def archiveData(processed_files, directory):
    proc_prefix = 'bkds_SubjGen'
    archive_dir = 'archive'

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_file = f'{proc_prefix}_{timestamp}.zip'
    archive_file = os.path.join(directory, archive_dir, archive_file)
    os.makedirs(os.path.dirname(archive_file), exist_ok=True)
    # Create a zip file and add processed files
    with zipfile.ZipFile(archive_file, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
            os.remove(file)  # Optionally remove the file after archiving

    print(f'Processed files are archived in {directory}')



def load_column_mappings(mapping_key):
    mapping_dir = os.path.join(bkds_util_data, 'config', 'bkds_data_mappings.json')

    print(f'load_column_mappings for {mapping_key} from {mapping_dir}')
    with open(mapping_dir, 'r') as file:
        data_list = json.load(file)

        if isinstance(data_list, list):
            print('isinstance')
            for template_entry in data_list:
                print('for template_entry in data_list')
                if mapping_key in template_entry:
                    template = template_entry[mapping_key]
                    print(f'mapping_key in template_entry: \n\n{template["target_schema"]}\n\n{template["target_table"]}')
                    target_schema = template["target_schema"]
                    target_table = template["target_table"]
                    target_columns = template["target_columns"]

                    placeholders = ', '.join(['%s'] * len(target_columns))
                    insert_query = f"INSERT INTO {target_schema}.{target_table} ({', '.join(target_columns)}) VALUES ({placeholders});"
                    print(f'\n{insert_query}')
                    return insert_query
            raise ValueError(f"No mapping found for key: {mapping_key}")
        else:
            raise TypeError("Expected a list in JSON data")

def split_text_into_spans(text):
    """
    Splits the input text into sentences, wraps each sentence in a <span> tag,
    and returns the processed HTML string.

    :param text: The input text to process.
    :return: Processed HTML string with sentences wrapped in <span> tags.
    """
    # Remove HTML tags
    text = re.sub(r'</?[^>]+(>|$)', '', text)

    # Detect Markdown-style headers (**header**) and replace with <strong> tags
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # Mark `\n\n` with a unique placeholder, e.g., `[NEWPARA]`, to preserve paragraph breaks
    text = re.sub(r'\n\n+', '[NEWPARA]', text)

    # Replace remaining single line breaks with spaces
    text = re.sub(r'\n', ' ', text)

    # Define abbreviations to avoid splitting in the middle of an abbreviation
    abbreviations = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Inc.', 'Ltd.', 'D.C.', 'U.S.']

    # Replace abbreviations with placeholders
    abbreviation_placeholders = {}
    for i, abbr in enumerate(abbreviations):
        placeholder = f'__ABBR{i}__'
        # Escape periods in abbreviations for regex
        abbr_escaped = re.escape(abbr)
        text = re.sub(abbr_escaped, placeholder, text)
        abbreviation_placeholders[placeholder] = abbr

    # Now we can split sentences at punctuation marks
    # Split sentences based on the regex
    sentence_end_regex = r'([.!?])\s+'
    sentences = re.split(sentence_end_regex, text)

    # Reconstruct sentences
    full_sentences = []
    i = 0
    while i < len(sentences):
        sentence = sentences[i].strip()
        if i + 1 < len(sentences):
            punctuation = sentences[i + 1]
            full_sentence = sentence + punctuation
            i += 2
        else:
            full_sentence = sentence
            i += 1
        full_sentences.append(full_sentence)

    # Restore abbreviations
    for i, sentence in enumerate(full_sentences):
        for placeholder, abbr in abbreviation_placeholders.items():
            full_sentences[i] = full_sentences[i].replace(placeholder, abbr)

    # Replace `[NEWPARA]` with `<br><br>` for visual line breaks
    merged_sentences = ' '.join([
        f'<span id="chunk-{index}">{sentence}</span>'
        for index, sentence in enumerate(full_sentences)
    ])
    merged_sentences = merged_sentences.replace('[NEWPARA]', '<br><br>')

    # Wrap the entire output in paragraph tags for structure
    return f'<p>{merged_sentences}</p>'
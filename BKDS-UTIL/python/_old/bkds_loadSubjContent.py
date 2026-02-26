"""
Subject Content Loader for Wiki Data

This script is designed to automate the process of loading structured content from JSON files into a PostgreSQL database. It specifically targets data related to wiki subjects, processing and storing detailed content from each subject entry.

Key Functionalities:
- Reads JSON files from a specified directory, each containing information about a wiki subject.
- Validates and processes the data from these files, including handling multiple image URLs and large text content.
- Inserts the processed data into a PostgreSQL table, `stg_subj_wiki_content`, in the `stg` schema.
- Each data insertion includes additional metadata: a unique load ID, the current timestamp as the load date, and the name of the load process.

Usage:
Execute the script with Python, optionally passing a filename pattern as an argument. Ensure all dependencies are installed and necessary environment variables are set.

Example:
    python script_name.py [optional_filename_pattern]
"""
import os
import json
import psycopg2
from datetime import datetime
import uuid
import sys
from bkdsUtilities import log_msg  # Assuming you're using the same logging utility

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
load_table = 'stg_subj_wiki_content'
load_schema = 'dev'
dat_dir='wiki'
######################################################################
# Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_LOAD_SUBJ_CONTENT', msg)
    print(msg)

# Database setup
db_params = {
    "host": "localhost",
    "database": "bkds",
    "user": "bkdsdev",
    "password": "hello"
}

# Function to create or replace the new target table
def create_or_replace_table(conn, load_table, load_schema):
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {load_schema}.{load_table} (
                    search_term TEXT,
                    insight_id TEXT,
                    category TEXT,
                    page_url TEXT,
                    images TEXT[],  -- Array to store multiple image URLs
                    extract TEXT,   -- Text field for potentially large content
                    subj_title TEXT,
                    load_id UUID,
                    load_process TEXT,
                    load_date TIMESTAMP,    
                    load_file TEXT
                );
            """)
            conn.commit()
        logMsg("Table created/replaced successfully.")
    except Exception as e:
        logMsg(f"Error in create_or_replace_table: {e}")
        raise

# Function to load JSON files based on optional pattern
def load_json_files(directory, load_id, load_table, pattern=None):
    logMsg(f'Starting to load JSON files from {directory}')
    conn = None
    try:
        conn = psycopg2.connect(**db_params)
        create_or_replace_table(conn, load_table, load_schema)
        for load_file in os.listdir(directory):
            #logMsg(f'load_file in  {load_file}')
            if load_file.endswith('.json') and (pattern is None or pattern in load_file):
                filepath = os.path.join(directory, load_file)
                logMsg(f'filepath {filepath}')
                logMsg(f'Processing file: {load_file}')
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    insert_data(data, conn, load_id, load_table, load_file)
        logMsg("JSON files loaded successfully.")
    except Exception as e:
        logMsg(f"Error in load_json_files: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logMsg("Database connection closed.")

# Helper function to validate UUID string
def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
        return str(uuid_obj) == uuid_to_test
    except ValueError:
        return False

# Function to insert data into the new table
def insert_data(data, conn, load_id, load_table, load_file):
    load_date = datetime.now()

    insert_query = f"""
    INSERT INTO {load_schema}.{load_table} (search_term, insight_id, category, page_url, images, extract, subj_title, load_id, load_process, load_date, load_file)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        with conn.cursor() as cur:
            # Check if data is a dictionary and not a list
            if isinstance(data, dict):
                data = [data]  # Convert to a list of one dictionary

            for item in data:
                # Directly use insightID as string
                insight_id = item.get('insightID', None)
                images = item.get('images', [])

                cur.execute(insert_query, (
                    item['searchTerm'], 
                    insight_id, 
                    item['category'], 
                    item['pageURL'], 
                    images, 
                    item['extract'], 
                    item['subjTitle'], 
                    load_id, 
                    program_name,
                    load_date, 
                    load_file
                ))
            conn.commit()
        logMsg("Data inserted into database successfully.")
    except Exception as e:
        logMsg(f"Error in insert_data: {e}")
        raise

def main():
    logMsg(f'in {program_name}')
    load_id = str(uuid.uuid4())
    proc_dir = os.getenv('BKDS_NODEJS_SUBJGEN', '/default/path/if/env/not/set')
    json_directory = os.path.join(proc_dir, dat_dir)

    # Use a command-line argument for the pattern or set it to None for loading all .json files
    pattern = sys.argv[1] if len(sys.argv) > 1 else None

    logMsg(f'Starting processing in directory: {json_directory}')
    load_json_files(json_directory, load_id, load_table, pattern)

if __name__ == "__main__":
    main()
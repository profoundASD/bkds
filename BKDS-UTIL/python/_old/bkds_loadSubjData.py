"""
Script Objective:
-----------------
This script loads JSON data into a PostgreSQL database. It first checks if the necessary table exists and creates it if not.
Then, it reads JSON files from a specified directory, extracts relevant data, and inserts it into the database.

High-Level Flow:
----------------
1. Set up database connection parameters.
2. Define functions for database table creation, JSON file loading, and data insertion.
3. In the main function, determine the directory for JSON files and invoke the loading process.
"""

import os
import json
import psycopg2
from datetime import datetime
import uuid
from bkdsLogMsg import log_msg
import sys

#########################   ############################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

load_table='stg_subj_gen_data'
load_schema='stg'

########################################################################
#  Main logic and functions


# Logging utility
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_GET_WIKI', msg)
    print(msg)

# PostgreSQL connection parameters
db_params = {
    "host": "localhost",
    "database": "bkds",
    "user": "bkdsdev",
    "password": "hello"
}

def create_or_replace_table(conn, load_table, load_schema):
    try:
        with conn.cursor() as cur:
            # Check if the table exists
            cur.execute(f"""
                SELECT EXISTS (
                    SELECT FROM pg_tables
                    WHERE  schemaname = '{load_schema}'
                    AND    tablename  = '{load_table}'
                );
            """)
            exists = cur.fetchone()[0]

            # Drop the table if it exists
            if exists:
                cur.execute(f"DROP TABLE {load_schema}.{load_table};")

            # Create the table
            cur.execute(f"""
                CREATE TABLE {load_schema}.{load_table} (
                    category TEXT,
                    keyword TEXT,
                    subject TEXT,
                    subjID TEXT,
                    load_id UUID,
                    file_id UUID,
                    LOAD_DATE TIMESTAMP,
                    LOAD_PROCESS TEXT,
                    LOAD_FILE TEXT
                );
            """)
            conn.commit()
        logMsg("Table created/replaced successfully.")
    except Exception as e:
        logMsg(f"Error in create_or_replace_table: {e}")
        raise

def load_json_files(directory, load_id, load_table):
    logMsg(f'Starting to load JSON files from {directory}')
    try:
        conn = psycopg2.connect(**db_params)
        create_or_replace_table(conn, load_table, load_schema)
        for load_file in filter(lambda f: f.endswith('.json'), os.listdir(directory)):
            filepath = os.path.join(directory, load_file)
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

def insert_data(data, conn, load_id, load_table, load_file):
    file_id = str(uuid.uuid4())
    load_date = datetime.now()

    program_name = os.path.basename(__file__)  # If needed in your data

    insert_query = f"""
    INSERT INTO {load_schema}.{load_table} (category, keyword, subject, subjID, load_id, file_id, load_date, load_process, load_file)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        with conn.cursor() as cur:
            for item in data:
                # Make sure you have 8 elements in this tuple to match the 8 placeholders
                cur.execute(insert_query, (item['category'], item['keyword'], item['subject'], item['subjID'], load_id, file_id, load_date, program_name, load_file))
            conn.commit()
        logMsg("Data inserted into database successfully.")
    except Exception as e:
        logMsg(f"Error in insert_data: {e}")
        raise

def main():
    load_id = str(uuid.uuid4())
    proc_dir = os.getenv('BKDS_NODEJS_PUBLIC', '/default/path/if/env/not/set')
    json_directory = os.path.join(proc_dir, 'data/subjects')
    logMsg(f'Starting processing in directory: {json_directory}')
    load_json_files(json_directory, load_id, load_table)

if __name__ == "__main__":
    main()

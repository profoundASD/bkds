import os
import json
import sys
import glob

from bkds_Utilities import log_msg, getHash, getDBConn, closeDB

program_name = os.path.basename(sys.argv[0])

def logMsg(msg):
    log_msg(program_name, 'BKDS_SUBJ_CONTENT_GEN', msg)
    print(msg)

# Directory containing JSON files
json_directory = os.environ.get('BKDS_UTIL_DATA', '/default/path/if/not/set')
json_directory = os.path.join(json_directory, 'GROUPALL/output/json')
logMsg(f"Directory for JSON files: {json_directory}")
file_match_pattern='GROUPALL'

# Function to create a table if it doesn't exist
def create_table(cursor):
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS dev.stg_subject_groups  (
            cluster_id INTEGER,
            record_id TEXT
        );
    """
    cursor.execute(create_table_sql)
    logMsg("Database table checked or created.")

def prepare_and_insert_json_data(json_data, cursor):
    logMsg('prepare_and_insert_json_data')
    # Insert each entry as a separate row
    for entry in json_data:
        logMsg(f'processing entry: {entry}')
        # Hash sensitive fields
        cluster_id = entry['cluster_id']
        record_id = entry['record_id']

        # Insert SQL
        insert_sql = """
        INSERT INTO dev.stg_subject_groups (cluster_id, record_id)
        VALUES (%s, %s);
        """
        cursor.execute(insert_sql, (cluster_id, record_id))

def load_json_files_to_db(directory):
    cursor, conn = getDBConn()
    try:
        create_table(cursor)
        conn.commit()

        # Find the latest file matching the pattern
        files = glob.glob(os.path.join(directory, f'*{file_match_pattern}*.json'))
        if files:
            latest_file = max(files, key=os.path.getmtime)
            logMsg(f"Loading data from latest file: {latest_file}")
            with open(latest_file, 'r') as file:
                json_data = json.load(file)
            prepare_and_insert_json_data(json_data, cursor)
            conn.commit()  # Commit the transaction after processing the file
            logMsg("Data committed to the database.")
        else:
            logMsg("No matching files found.")

        
        conn.commit()  # Commit the transaction after all files are processed
        logMsg("All data committed to the database.")
    except Exception as e:
        logMsg(f"An error occurred: {e}")
        conn.rollback()  # Roll back in case of error
    finally:
        closeDB(cursor, conn)

# Main execution
if __name__ == "__main__":
    load_json_files_to_db(json_directory)

import os
import json
import sys

from bkdsUtilities import log_msg, getHash, getDBConn, closeDB

program_name = os.path.basename(sys.argv[0])

def logMsg(msg):
    log_msg(program_name, 'BKDS_SUBJ_CONTENT_GEN', msg)
    print(msg)

# Directory containing JSON files
json_directory = os.environ.get('BKDS_UTIL_DATA')
logMsg("Initial directory: " + json_directory)
json_directory = os.path.join(json_directory, 'subjGen/wipSubj')
logMsg("Final directory: " + json_directory)

# Function to create a table if it doesn't exist
def create_table(cursor):
    create_table_sql = """
                CREATE TABLE IF NOT EXISTS dev.tbl_subject_load_flat (
                    data_category TEXT,
                    data_subject TEXT,
                    file_id TEXT,
                    insight_id TEXT,
                    load_date TEXT,
                    load_file TEXT,
                    load_id TEXT,
                    load_process TEXT,
                    page_url TEXT,
                    record_id TEXT,
                    search_id TEXT,
                    search_term TEXT,
                    src_insight_id TEXT,
                    src_subject_id TEXT,
                    subject_title TEXT,
                    wiki_subj_id TEXT,
                    trait1 TEXT
                    );
                    """
    cursor.execute(create_table_sql)

def prepare_json_data(json_data):
    # Set data_trait1 if available in any of the entries' trait1
    first_trait1 = next((entry.get('trait1') for entry in json_data['entries'] if entry.get('trait1')), None)
    if first_trait1:
        json_data['data_trait1'] = first_trait1
    else:
        json_data['data_trait1'] = "default_value"  # Use a default value or handle as needed

    #json_data['data_subject'] = json.dumps(json_data['data_subject'])
    json_data['data_subject']=first_trait1

    # Process entries before serializing them to JSON
    processed_entries = []
    for entry in json_data['entries']:
        entry_data = {
            "search_term": entry['search_term'],
            "trait1": entry['trait1']
        }
        processed_entries.append(entry_data)

    # Now serialize the processed entries
    json_data['entries'] = json.dumps(processed_entries)

    # Apply hashing to necessary fields
    for key in ['file_id', 'insight_id', 'load_id', 'record_id', 'search_id', 'src_insight_id', 'src_subject_id']:
        if key in json_data:
            json_data[key] = getHash(json_data[key])

    # Note: Do not attempt to pop from json_data['entries'] after this point as it is now a string
def prepare_and_insert_json_data(json_data, cursor):
    # Set data_category from JSON, or use default if missing
    data_category = json_data.get('data_category', 'default_category')
    
    # Serialize data_subject to JSON string
    data_subject = json.dumps(json_data.get('data_subject', []))
    
    # Prepare common fields for hashing
    common_fields = {
        'file_id': json_data.get('file_id'),
        'insight_id': json_data.get('insight_id'),
        'load_id': json_data.get('load_id'),
        'record_id': json_data.get('record_id'),
        'search_id': json_data.get('search_id'),
        'src_insight_id': json_data.get('src_insight_id'),
        'src_subject_id': json_data.get('src_subject_id'),
    }

    # Apply hashing
    for key, value in common_fields.items():
        if value:
            common_fields[key] = getHash(value)

    # Insert each entry as a separate row
    for entry in json_data['entries']:
        trait1 = entry.get('trait1', 'default_trait')
        search_term = entry.get('search_term', 'default_search_term')

        # Insert SQL
        insert_sql = """
        INSERT INTO dev.tbl_subject_load_flat (
            data_category, data_subject, file_id, insight_id, load_date, load_file,
            load_id, load_process, page_url, record_id, search_id, search_term,
            src_insight_id, src_subject_id, subject_title, wiki_subj_id, trait1
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_sql, (
            data_category, trait1, common_fields['file_id'], common_fields['insight_id'], 
            json_data.get('load_date'), json_data.get('load_file'), common_fields['load_id'], 
            json_data.get('load_process'), json_data.get('page_url'), common_fields['record_id'], 
            common_fields['search_id'], search_term, common_fields['src_insight_id'], 
            common_fields['src_subject_id'], json_data.get('subject_title'), 
            json_data.get('wiki_subj_id'), trait1
        ))


def load_json_files_to_db(directory):
    cursor, conn = getDBConn()
    try:
        create_table(cursor)  # Ensure the new flat table exists
        conn.commit()

        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r') as file:
                    json_data = json.load(file)

                # Prepare and insert data
                prepare_and_insert_json_data(json_data, cursor)
        conn.commit()  # Commit the transaction
    except Exception as e:
        logMsg(f"An error occurred: {e}")
        conn.rollback()  # Roll back in case of error
    finally:
        closeDB(cursor, conn)

# Main execution
load_json_files_to_db(json_directory)

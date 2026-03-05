import os
import hashlib
import time
import argparse
import psycopg2
from datetime import datetime
from bkdsUtilities import log_msg, getDBConn, closeDB, get_sqlTemplate, fetch_data

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("--low", type=float, default=3, help="Minimum sleep time in seconds")
    parser.add_argument("--high", type=float, default=10, help="Maximum sleep time in seconds")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id

# Set environment variables or replace with actual paths
util_data = os.getenv('BKDS_UTIL_DATA')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

content_root = 'image'
target_dir = os.path.join(nodejs_data, content_root)
target_schema = 'dev'
target_obj = 'stg_img_cache'
target_table = f'{target_schema}.{target_obj}'
template_key = 'bkds_imgCaceGen_load'
suppress_template_key = 'bkds_imgCaceGen_stg_select'
image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
small_img = 'PIL_480'
med_img = 'PIL_720'
large_img = 'PIL_1080'
img_type = 'jpg'
print(f'query_key {template_key}')

mapping_source_type = 'img_cache'

########################################################################
# Main logic and functions
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def sanitize_filename(filename):
    """Sanitize the filename by removing unsafe characters and replacing spaces with underscores."""
    return filename.replace(' ', '_').replace("'", "''")

def generate_md5_hash(*args):
    """Generate an MD5 hash from multiple string inputs."""
    hash_obj = hashlib.md5()
    combined_string = "".join(args).encode('utf-8')
    hash_obj.update(combined_string)
    return hash_obj.hexdigest()

def build_insert_statements(target_directory):
    data_to_insert = []
    load_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    load_proc = program_name
    sequence_number = 0

    for root, dirs, files in os.walk(target_directory):
        if 'pil' in dirs:
            dirs.remove('pil')  # Exclude the 'pil' directory

        for file in files:
            if file.lower().endswith(image_extensions):
                img_path = os.path.join(root, file)
                img_type = os.path.basename(root)
                img_name = sanitize_filename(file)
                data_source = img_name.split('_')[1]
                img_url_id = img_name.split('_')[2]

                pil_dir = os.path.join(target_directory, 'pil')
                img_small_path = os.path.join(pil_dir, f"{img_url_id}_{small_img}.{img_type}")
                img_medium_path = os.path.join(pil_dir, f"{img_url_id}_{med_img}.{img_type}")
                img_large_path = os.path.join(pil_dir, f"{img_url_id}_{large_img}.{img_type}")

                load_key = generate_md5_hash(img_url_id, img_name, img_path, load_date)

                record = (
                    img_url_id, img_name, img_type, img_path, img_small_path, img_medium_path,
                    img_large_path, data_source, load_date, load_proc, load_key, sequence_number, batch_id
                )
                data_to_insert.append(record)
                sequence_number += 1

    return data_to_insert

def prepare_and_insert_json_data(json_data, cursor):
    logMsg('prepare_and_insert_json_data')
    # Define the insert SQL
    insert_sql = f"""
    INSERT INTO {target_table} (IMG_URL_ID, IMG_NAME, IMG_TYPE, IMG_PATH, IMG_SMALL_PATH, IMG_MEDIUM_PATH, IMG_LARGE_PATH, DATA_SOURCE, LOAD_DATE, LOAD_PROC, LOAD_KEY, LOAD_SEQ, BATCH_ID)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    # Insert each entry as a separate row
    for entry in json_data:
        logMsg(f'processing entry: {entry}')
        cursor.execute(insert_sql, (
            entry[0], entry[1], entry[2], entry[3], entry[4],
            entry[5], entry[6], entry[7], entry[8],
            entry[9], entry[10], entry[11], entry[12]
        ))

def main(target_directory):
    data_to_insert = build_insert_statements(target_directory)
    
    # Fetch IDs to suppress
    sql_query = get_sqlTemplate(suppress_template_key)
    suppress_data = fetch_data(sql_query)  # Fetch data using the SQL query
    suppress_ids = set(record['img_url_id'] for record in suppress_data)
    
    # Filter out suppressed IDs
    data_to_insert = [record for record in data_to_insert if record[0] not in suppress_ids]
    logMsg(f"{len(data_to_insert)} records to be inserted after suppression")

    cursor, conn = getDBConn()
    try:
        prepare_and_insert_json_data(data_to_insert, cursor)
        conn.commit()
        logMsg(f"Inserted {len(data_to_insert)} records into {target_table}")
    except Exception as e:
        conn.rollback()
        logMsg(f"Failed to insert records: {e}")
    finally:
        closeDB(cursor, conn)

# If this script is standalone, use it like this:
if __name__ == "__main__":
    main(target_dir)

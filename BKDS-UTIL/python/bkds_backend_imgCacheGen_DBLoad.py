import os
import hashlib
import time
import argparse
import psycopg2
from datetime import datetime
from PIL import Image
from bkds_Utilities import log_msg, getDBConn, closeDB, get_sqlTemplate, fetch_data

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)

content_root = 'image_cache'
target_schema = 'dev'
target_obj = 'stg_img_cache'
target_table = f'{target_schema}.{target_obj}'
template_key = 'bkds_imgCaceGen_load'
suppress_template_key = 'bkds_imgCaceGen_stg_select'
image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
sizes = ['PIL_480', 'PIL_720', 'PIL_1080']
valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
thumb_dir = 'thumbnail'
mapping_source_type = 'img_cache'

########################################################################
# Main logic and functions
def logMsg(msg, batch_id):
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

def generate_thumbnails(source_directory):
    generated_count = 0
    skipped_count = 0

    # Gather all files in the directory that do not have _PIL_ in the name
    base_files = [f for f in os.listdir(source_directory) if os.path.isfile(os.path.join(source_directory, f)) and "_PIL_" not in f]

    print(f"Found {len(base_files)} base files to process.")

    for base_file in base_files:
        base_name, ext = os.path.splitext(base_file)

        # Skip non-image files
        if ext.lower() not in valid_extensions:
            print(f"Skipping non-image file: {base_file}")
            continue

        for size in sizes:
            suffix = f"_{size}.jpg"
            pil_version = base_name + suffix
            pil_path = os.path.join(source_directory, pil_version)

            # If the _PIL_ version does not exist, create it
            if not os.path.exists(pil_path):
                img_path = os.path.join(source_directory, base_file)
                
                try:
                    with Image.open(img_path) as img:
                        img_copy = img.copy()
                        img_copy.thumbnail((int(size.split('_')[1]), int(size.split('_')[1])), Image.LANCZOS)
                        img_copy.save(pil_path)
                        print(f"Created {pil_path}")
                        generated_count += 1
                except Exception as e:
                    print(f"Failed to create {pil_path}: {e}")
            else:
                print(f"Skipped existing file: {pil_path}")
                skipped_count += 1

    print(f"Total files generated: {generated_count}")
    print(f"Total files skipped: {skipped_count}")

def build_insert_statements(target_directory, batch_id):
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

                if '_PIL_' in file:
                    continue  # Skip files with _PIL_ in their name

                base_name, ext = os.path.splitext(file)
                img_file_type = ext.lstrip('.').lower()  # Remove leading dot and convert to lowercase

                img_name = sanitize_filename(file)
                components = img_name.split('_')
                if len(components) < 3:
                    print(f"Skipping file with insufficient components: {file}")
                    continue

                img_type = components[0]
                data_source = components[1]
                img_url_id = components[2]

                img_small_path = os.path.join(target_directory, f"{base_name}_PIL_480.{img_file_type}")
                img_medium_path = os.path.join(target_directory, f"{base_name}_PIL_720.{img_file_type}")
                img_large_path = os.path.join(target_directory, f"{base_name}_PIL_1080.{img_file_type}")
                print(img_small_path)
                print(img_medium_path)
                print(img_large_path)
                
                load_key = generate_md5_hash(img_url_id, img_name, img_path, load_date)

                record = (
                    img_url_id, img_name, img_file_type, img_path, img_small_path, img_medium_path,
                    img_large_path, data_source, load_date, load_proc, load_key, sequence_number, batch_id
                )
                data_to_insert.append(record)
                sequence_number += 1

    return data_to_insert

def prepare_and_insert_json_data(json_data, cursor, batch_id):
    logMsg('prepare_and_insert_json_data', batch_id)
    # Define the insert SQL
    insert_sql = f"""
    INSERT INTO {target_table} (IMG_URL_ID, IMG_NAME, IMG_TYPE, IMG_PATH, IMG_SMALL_PATH, IMG_MEDIUM_PATH, IMG_LARGE_PATH, DATA_SOURCE, LOAD_DATE, LOAD_PROC, LOAD_KEY, LOAD_SEQ, BATCH_ID)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    # Insert each entry as a separate row
    for entry in json_data:
        logMsg(f'processing entry: {entry}', batch_id)
        cursor.execute(insert_sql, (
            entry[0], entry[1], entry[2], entry[3], entry[4],
            entry[5], entry[6], entry[7], entry[8],
            entry[9], entry[10], entry[11], entry[12]
        ))

def loadDB(batch_id, target_directory):
    data_to_insert = build_insert_statements(target_directory, batch_id)
    
    # Fetch IDs to suppress
    sql_query = get_sqlTemplate(suppress_template_key)
    suppress_data = fetch_data(sql_query)  # Fetch data using the SQL query
    suppress_ids = set(record['img_url_id'] for record in suppress_data)
    
    # Filter out suppressed IDs
    data_to_insert = [record for record in data_to_insert if record[0] not in suppress_ids]
    logMsg(f"{len(data_to_insert)} records to be inserted after suppression", batch_id)

    cursor, conn = getDBConn()
    try:
        prepare_and_insert_json_data(data_to_insert, cursor, batch_id)
        conn.commit()
        logMsg(f"Inserted {len(data_to_insert)} records into {target_table}", batch_id)
    except Exception as e:
        conn.rollback()
        logMsg(f"Failed to insert records: {e}", batch_id)
    finally:
        closeDB(cursor, conn)

# Add a function to parse arguments for standalone mode
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("target_directory", help="Target directory")
    return parser.parse_args()

# Allow the script to be run standalone
if __name__ == "__main__":
    args = parse_arguments()
    loadDB(args.batch_id, args.target_directory)
    generate_thumbnails(args.target_directory)

import requests
import json
from datetime import datetime, timedelta
from bkds_Utilities import log_msg
import os
import sys
import socket
import zipfile

#####################################################################
# Main Setup / Variables
hostname = socket.gethostname()
batch_id = sys.argv[1]
rpt_type='BKDS_REPORTING_DATA'
program_name = f"{os.path.basename(sys.argv[0])}"
#puts reoprt into folder / file derived from hostname/batch id's passed in for reporting
#categorize by host
out_dir = os.getenv(rpt_type)
#report
node_id=os.path.join(out_dir,  hostname)
os.makedirs(node_id, exist_ok=True)
#categorize by date
rpt_folder = os.path.join(node_id, datetime.now().strftime("%Y%m%d"))
#categorize type (speed stats/ software stats etc)
rpt_type_folder=f'{batch_id}'
rpt_folder = os.path.join(rpt_folder,rpt_type_folder)
os.makedirs(rpt_folder, exist_ok=True)
###set up output file names
raw_type="raw"
parsed_type="insight"
out_type ="json"

raw_out_file = os.path.join(
    out_dir, 
    rpt_folder,
    f"{hostname}_{batch_id}_{program_name}_{raw_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{out_type}"
)

parsed_out_file = os.path.join(
    out_dir, 
    rpt_folder,
    f"{hostname}_{batch_id}_{program_name}_{parsed_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{out_type}"
)

archive_dir = os.path.join(rpt_folder, "archive")
os.makedirs(archive_dir, exist_ok=True)

API_SOURCE_URL='https://fdo.rocketlaunch.live/json/launches/next'
API_RESP_GOOD=200

# Global variables for JSON keys
KEY_ID = 'id'
KEY_NAME = 'name'
KEY_PAD = 'pad'
KEY_LOCATION = 'location'
KEY_COUNTRY = 'country'
KEY_T0 = 't0'
KEY_TAGS = 'tags'
KEY_TEXT = 'text'
KEY_QUICKTEXT = 'quicktext'
KEY_MODIFIED = 'modified'
KEY_DESC = 'description'
KEY_LAUNCH_DESC = 'launch_description'
DAY_LIMIT = 10  # Number of days to consider for archiving old .json files
KEY_RESULT='result'
# Parsed data keys
PARSED_KEY_MISSION_ID = "launch_mission_id"
PARSED_KEY_MISSION = "launch_mission"
PARSED_KEY_PAD_ID = "launch_pad_id"
PARSED_KEY_PAD_NAME = "launch_pad_name"
PARSED_KEY_PAD_COUNTRY = "launch_pad_country"
PARSED_KEY_DESC = "launch_desc"
PARSED_KEY_EST_TIME = "launch_est_time"
PARSED_KEY_PURPOSE = "launch_purpose"
PARSED_KEY_QUICKTEXT = "launch_quicktext"
PARSED_KEY_LAST_UPDATE = "launch_last_update"
PARSED_KEY_SUBJECT_TITLE = "subject_title"

subject_title='Rocket Launch Update'
########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), batch_id, msg)
    print(msg)


def split_string_by_length(s, max_width):
    words = s.split()
    lines = []
    current_line = []

    for word in words:
        # Check if adding the next word exceeds the max width
        if len(' '.join(current_line + [word])) <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line
    lines.append(' '.join(current_line))

    return lines

# Global Variables

def archive_data():
    """Archives all files containing 'raw' (case-insensitive) in their name 
    and all .json files older than the specified DAY_LIMIT in the current directory."""
    logMsg(f"archive_data() started")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = os.path.join(archive_dir, f"{program_name}_{timestamp}.zip")
    
    # Calculate the cutoff time for old files
    cutoff_time = datetime.now() - timedelta(days=DAY_LIMIT)
    files_to_archive = []

    # Identify files to archive
    for file in os.listdir(rpt_folder):
        file_path = os.path.join(rpt_folder, file)

        # Ensure it's a file and not a directory
        if not os.path.isfile(file_path):
            continue
        
        # Get the last modification time of the file
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Check if 'raw' (case-insensitive) is in the filename or if the file is a .json older than DAY_LIMIT
        if (raw_type.lower() in file.lower() or file.endswith('.json') and file_mtime < cutoff_time):
            files_to_archive.append(file_path)

    # Create the ZIP file only if there are files to archive
    if files_to_archive:
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file_path in files_to_archive:
                zipf.write(file_path, arcname=os.path.basename(file_path))
                os.remove(file_path)  # Optionally delete the original file
                logMsg(f"Archived and removed file: {os.path.basename(file_path)}")
        logMsg(f"Archive created: {zip_filename}")
    else:
        logMsg("No files to archive. No ZIP file created.")


def ordinal_suffix_of(i):
    j = i % 10
    k = i % 100
    if j == 1 and k != 11:
        return f"{i}st"
    if j == 2 and k != 12:
        return f"{i}nd"
    if j == 3 and k != 13:
        return f"{i}rd"
    return f"{i}th"

def fetch_and_process_rocket_launch_data():
    response = requests.get(API_SOURCE_URL)
    logMsg(f"fetch_and_process_rocket_launch_data with url: {API_SOURCE_URL}")
    logMsg(f"API RESPONSE\n {response}")

    if response.status_code == API_RESP_GOOD:
        try:
            data = response.json()
            logMsg(f"API JSON cleared data")
        except json.JSONDecodeError:
            logMsg(f"Failed to parse JSON. Raw response content:\n{response.text}")
            with open(f"{raw_out_file}_error.log", "w") as file:
                file.write(response.text)
            logMsg(f"Raw response saved to {raw_out_file}_error.log")
            return

        if data is None or "error" in json.dumps(data, ensure_ascii=False, default=str).lower():
            logMsg(f"{raw_type} data is null or contains an error.")
        else:
            with open(f'{raw_out_file}', 'w') as file:
                json.dump(data, file, indent=4)
            logMsg(f"{raw_type} data saved to {raw_out_file}")

        launch_data = data[KEY_RESULT][0]
        launch_description = launch_data.get(KEY_LAUNCH_DESC, '')
        formatted_launch_desc = '\n'.join(split_string_by_length(launch_description, 40))
        parsed_data = {
            PARSED_KEY_MISSION_ID: launch_data.get(KEY_ID),
            PARSED_KEY_MISSION: launch_data.get(KEY_NAME),
            PARSED_KEY_PAD_ID: launch_data[KEY_PAD][KEY_ID] if launch_data.get(KEY_PAD) else None,
            PARSED_KEY_PAD_NAME: launch_data[KEY_PAD][KEY_LOCATION][KEY_NAME] if launch_data.get(KEY_PAD) else None,
            PARSED_KEY_PAD_COUNTRY: launch_data[KEY_PAD][KEY_LOCATION].get(KEY_COUNTRY) if launch_data.get(KEY_PAD) else None,
            PARSED_KEY_DESC: formatted_launch_desc,
            PARSED_KEY_EST_TIME: launch_data.get(KEY_T0),
            PARSED_KEY_PURPOSE: launch_data[KEY_TAGS][0][KEY_TEXT] if launch_data.get(KEY_TAGS) else None,
            PARSED_KEY_QUICKTEXT: launch_data.get(KEY_QUICKTEXT),
            PARSED_KEY_LAST_UPDATE: launch_data.get(KEY_MODIFIED),
            PARSED_KEY_SUBJECT_TITLE: subject_title
        }
        parsed_data = {k: v for k, v in parsed_data.items() if v is not None}
        with open(parsed_out_file, 'w') as file:
            json.dump(parsed_data, file, indent=4)
        logMsg(f"{parsed_type} data saved to {parsed_out_file}")
    else:
        logMsg(f"Failed to retrieve {raw_type} data. Status code: {response.status_code}")


        
def main():

    logMsg(f"targeting: {raw_type} output file: {raw_out_file}")
    logMsg(f"targeting: {parsed_type} output file: {parsed_out_file}")
    
    logMsg(f"getting rocket launch data...\n")
    fetch_and_process_rocket_launch_data()
    
    logMsg(f"archiving data...\n")
    archive_data()

if __name__ == "__main__":
    main()

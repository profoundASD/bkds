import requests
import json
from datetime import datetime
from bkds_Utilities import log_msg
import os
import sys
import socket

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
rpt_type_folder=f'{rpt_type}_{batch_id}'
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

########################################################################
#  Main logic and functions

def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_AUTO_SCHED', msg)
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
    url = 'https://fdo.rocketlaunch.live/json/launches/next'
    response = requests.get(url)
    logMsg(f"using {url}")

    if response.status_code == 200:
        data = response.json()
        
        # Check if the data is null or contains the word "error" (case-insensitive)
        if data is None or "error" in json.dumps(data, ensure_ascii=False, default=str).lower():
            logMsg(f"{raw_type} data is null or contains an error.")
        else:
            # Save the full data to a JSON file
            with open(f'{raw_out_file}', 'w') as file:
                json.dump(data, file, indent=4)
            
            logMsg(f"{raw_type} data saved to {raw_out_file}")
        
        logMsg(f"{raw_type} data saved to {raw_out_file}")

        # Extracting the desired fields
        launch_data = data['result'][0]
        launch_description = launch_data.get('launch_description', '')

        # Split the launch description into lines and join back with newlines
        max_line_length = 40  # Adjust the line length as needed
        formatted_launch_desc = split_string_by_length(launch_description, max_line_length)
        formatted_launch_desc_str = '\n'.join(formatted_launch_desc)

        parsed_data = {
            "launch_mission_id": launch_data.get('id'),
            "launch_mission": launch_data.get('name'),
            "launch_pad_id": launch_data['pad']['id'] if launch_data.get('pad') else None,
            "launch_pad_name": launch_data['pad']['location']['name'] if launch_data.get('pad') else None,
            "launch_pad_country": launch_data['pad']['location'].get('country') if launch_data.get('pad') and launch_data['pad']['location'].get('country') else None,
            "launch_desc": formatted_launch_desc_str,  # Assign the formatted string here
            "launch_est_time": launch_data.get('t0'),
            "launch_purpose": launch_data['tags'][0]['text'] if launch_data.get('tags') else None,
            "launch_quicktext": launch_data.get('quicktext'),
            "launch_last_update": launch_data.get('modified')
        }

        parsed_data = {k: v for k, v in parsed_data.items() if v is not None}
        with open(parsed_out_file, 'w') as file:
            json.dump(parsed_data, file, indent=4)
        logMsg(f"{parsed_type} data saved to {parsed_out_file}")
    else:
        logMsg(f"Failed to retrieve {raw_type} data. Status code: {response.status_code}")


        #logMsg(f"data: {parsed_data}")
def main():
    logMsg(f"targeting: {raw_type} output file: {raw_out_file}")
    logMsg(f"targeting: {parsed_type} output file: {parsed_out_file}")
    
    fetch_and_process_rocket_launch_data()
    
if __name__ == "__main__":
    main()

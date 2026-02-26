"""
    usage:
    purpose:
    misc:
"""
import json
import subprocess
import os
from datetime import datetime
import sys
import socket
import time

bkds_util_python = os.environ.get('BKDS_UTIL_PYTHON')
# Check if the environment variable is set
if bkds_util_python:
    # Append the directory path to sys.path
    sys.path.append(bkds_util_python)
else:
    # Handle the case where the environment variable is not set
    print("BKDS_UTIL_PYTHON environment variable is not set.")

print(f'bkds_util_pyton {bkds_util_python}')
print(f'sys.path: {sys.path}')

#yfrom bkdsLogMsg import log_msg
from bkds_Utilities import log_msg

#####################################################################
# Main Setup / Variables
hostname = socket.gethostname()
batch_id = sys.argv[1]
ref_stats_json = sys.argv[2]
rpt_type='BKDS_REPORTING_DATA'
out_dir = os.getenv(rpt_type)
#puts reoprt into folder / file derived from hostname/batch id's passed in for reporting
#categorize by host
node_id=os.path.join(out_dir,  hostname)
#report
os.makedirs(node_id, exist_ok=True)
#categorize by date
rpt_folder = os.path.join(node_id, datetime.now().strftime("%Y%m%d"))
#categorize type (speed stats/ software stats etc)
rpt_type_folder=f'{rpt_type}_{batch_id}'
rpt_folder = os.path.join(rpt_folder,rpt_type_folder)
os.makedirs(rpt_folder, exist_ok=True)
###set up output file names
bkds_stats_output = os.path.join(
    out_dir, 
    rpt_folder,
    f"{hostname}_{batch_id}_{os.path.basename(sys.argv[0])}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
)



def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), rpt_type, msg)
    print(msg)


########################################################################
#  Main logic and functions

def generate_shell_script(config):
    script_lines = [""]
    for key, value in config.items():
        if value["required"]:
            # Add a line to print the timestamp before each command
            script_lines.append(f'echo "Running {key} at $(date)"')
            # Construct the script line
            script_line = f'{key}="$({value["command"]})"; echo "{key}: ${{{key}}}"'
            script_lines.append(script_line)
            
    script_lines.append("echo \"Script completed at $(date)\"")
    return "\n".join(script_lines)

def run_shell_script(script):
    process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    output_lines = []
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logMsg(output.strip())
            output_lines.append(output.strip())

    return_code = process.poll()
    full_output = '\n'.join(output_lines)
    return full_output

def parse_output_to_json(output, start_ts):
    result = {}
    for line in output.split('\n'):
        if ": " in line:
            key, value = line.split(": ", 1)
            # Skip any keys or values with "ERROR", "null", or suspiciously short entries
            if "ERROR" in value or value.strip().lower() == "null" or len(value.strip()) < 10:
                continue  # <-- Skip the line instead of returning None
            result[key] = value

    if result:  # Ensure we have valid key-value pairs
        result["start_utc_ts"] = start_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        result["end_utc_ts"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return result
    return None

def main():
    start_timestamp = datetime.utcnow()
    logMsg(f"Start - Timestamp: {start_timestamp}")
    
    # Load config file
    try:
        with open(ref_stats_json, 'r') as file:
            config = json.load(file)
    except Exception as e:
        logMsg(f"Failed to load configuration: {e}")
        return

    # Generate and execute the shell script
    shell_script = generate_shell_script(config)
    shell_output = run_shell_script(shell_script)

    # Parse the output
    result = parse_output_to_json(shell_output, start_timestamp)#
    #print('\n\nShowing results')
    #print(result)
    #time.sleep(10)
    #print(shell_output)
    #time.sleep(10)

    if not result:
        logMsg("No valid data to write. Skipping file creation.")
        return
    
    
    # Ensure the output directory exists
    out_dir = os.path.dirname(bkds_stats_output)
    os.makedirs(out_dir, exist_ok=True)

    # Write results to the target file
    try:
        with open(bkds_stats_output, 'w') as outfile:
            json.dump(result, outfile, indent=4)
        logMsg(f"Results written to {bkds_stats_output}")
    except Exception as e:
        logMsg(f"Failed to write results: {e}")

if __name__ == "__main__":
    main()
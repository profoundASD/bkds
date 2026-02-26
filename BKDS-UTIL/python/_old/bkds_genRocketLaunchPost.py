import os
import glob
import json
from datetime import datetime
import argparse
import socket

def parse_arguments():
    parser = argparse.ArgumentParser(description="Aggregate rocket launch data and generate a consolidated output JSON file.")
    parser.add_argument("batch_id", help="Batch ID for the current run")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
program_name = os.path.basename(__file__)

util_data = os.getenv('BKDS_AUTO')
nodejs_data = os.getenv('BKDS_NODEJS_DATA')

hostname = socket.gethostname()
hostname='bkds-pc-00x'
current_date = datetime.now().strftime('%Y%m%d')


# Directory paths
json_dir = "./launch_data"  # Directory containing JSON files
output_dir = "./formatted_launch"  # Directory for formatted HTML output

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Find the latest JSON file in the directory
json_files = glob.glob(os.path.join(json_dir, "*.json"))
if not json_files:
    print("No JSON files found in the directory.")
    exit()

latest_json = max(json_files, key=os.path.getctime)

# Parse JSON data
with open(latest_json, 'r') as file:
    data = json.load(file)

# Extract fields
launch_data = data.get("result", [])[0]  # Get the first result item

# Use alternate fields if primary field is missing
launch_name = launch_data.get("name") or (launch_data.get("missions")[0].get("name") if launch_data.get("missions") else "N/A")
launch_vehicle = launch_data.get("vehicle", {}).get("name", "N/A")
launch_pad = launch_data.get("pad", {}).get("name", "N/A")
launch_location = launch_data.get("pad", {}).get("location", {})
launch_desc = launch_data.get("launch_description", "N/A")
launch_detail = launch_data.get("quicktext", "N/A")

# Format HTML
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Launch Information</title>
</head>
<body>
    <h2>Launch Overview</h2>
    <p><strong>Launch Name:</strong> {launch_name}</p>
    <p><strong>Launch Vehicle:</strong> {launch_vehicle}</p>
    <h3>Launch Pad</h3>
    <ul>
        <li><strong>Name:</strong> {launch_pad}</li>
        <li><strong>Location:</strong> {launch_location.get("name", "N/A")}</li>
        <li><strong>State:</strong> {launch_location.get("state", "N/A")}</li>
        <li><strong>State Name:</strong> {launch_location.get("statename", "N/A")}</li>
        <li><strong>Country:</strong> {launch_location.get("country", "N/A")}</li>
    </ul>
    <h3>Mission Summary</h3>
    <p>{launch_desc}</p>
    <h3>Additional Details</h3>
    <p>{launch_detail}</p>
</body>
</html>
"""

# Save HTML to file
output_path = os.path.join(output_dir, "launch_overview.html")
with open(output_path, 'w') as output_file:
    output_file.write(html_content)

print(f"HTML content saved to {output_path}")

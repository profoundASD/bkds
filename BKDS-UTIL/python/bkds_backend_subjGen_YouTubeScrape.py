import pyautogui
import random
import time
import glob
import time
import json
import os
import re
from datetime import datetime
import webbrowser
from bkds_Utilities import log_msg, fetch_data, get_sqlTemplate
#####################################################################
# Main Setup / Variables
# Setup logging and SQL query fetching from utilities
program_name = os.path.basename(__file__)
batch_id = 'SUBJ_GEN_YOUTUBE_SCRAPE'
query_key = 'bkds_subjGen_source_index_wip'
directory = os.path.dirname(os.path.abspath(__file__))
dl_directory = os.path.expanduser('~/vmMate00/vmMate00_ytScrape')

browser_type = "firefox"
url="https://youtube.com"

#print(f'query_key {query_key}')
sql_query = get_sqlTemplate(query_key)
sql_query = '''
SELECT distinct subject_id, insight_id, search_id, search_term, data_category, subject
FROM dev.v_subject_gen_source  a
left join  dev.stg_youtube_api_results b
on ltrim(rtrim(coalesce(b.searchid  , '$')))  = ltrim(rtrim(coalesce(a.search_id , '$'))) 
left join  dev.stg_youtube_api_results c
on ltrim(rtrim(coalesce(a.search_term  , '$')))  = ltrim(rtrim(coalesce(c.searchterm , '$'))) 
left join  dev.stg_youtube_api_results d
on ltrim(rtrim(coalesce(a.orig_search_term  , '$')))  = ltrim(rtrim(coalesce(d.searchterm , '$'))) 
left join  dev.stg_youtube_api_results e
on ltrim(rtrim(coalesce(a.insight_id  , '$')))  = ltrim(rtrim(coalesce(e.insightid , '$'))) 
where c.videourl is null
and b.videourl is null
and e.videourl is null
and d.videourl is null
and length(a.subject_id) > 0
'''
#print(f'using sql_query {sql_query}')

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f'search_terms_{timestamp}.json'

########################################################################
#  Main logic and functions

def get_latest_json_file(directory=None, pattern='search_terms_*.json'):
    if directory is None:
        # Set directory to the directory of the currently running script
        directory = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full pattern to search for
    search_pattern = os.path.join(directory, pattern)
    print(f'search_pattern: {search_pattern} from {directory}')
    # List all files matching the pattern
    files = glob.glob(search_pattern)
    
    # Sort files by their modification time in descending order
    latest_file = max(files, key=os.path.getmtime, default=None)
    
    # Return the path to the latest file, or None if no files were found
    return latest_file


def generate_search_url(term_dict):
    """Generate a YouTube search URL for a given term."""
    # Assuming 'term' is the key that contains the search term string.
    # Adjust the key name according to your actual data structure.
    search_term = term_dict['term'] if 'term' in term_dict else str(term_dict)
    search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
    return search_url

def type_commands(search_term):
    """Type specific keyboard commands for each search URL."""
    time.sleep(2)
    pyautogui.press('/')  # Press '/' to activate search
    time.sleep(1)
    pyautogui.press('backspace')  # Press backspace
    time.sleep(1)
    pyautogui.typewrite(search_term)  # Type the search URL
    time.sleep(1)
    pyautogui.press('enter')  # Press enter to initiate search
    time.sleep(2)
    pyautogui.hotkey('ctrl', 's')  # Press Ctrl+S to save
    time.sleep(2)
    pyautogui.press('enter')  # Press enter to confirm save
    time.sleep(2)
    pyautogui.press('/')  # Press '/' to activate search
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'a')  # Press Ctrl+S to save
    time.sleep(2)
    pyautogui.press('backspace')  # Press backspace

def open_url(url, browser_type):
    print(f"Opening URL: {url} with {browser_type}")
    # First, try to kill any existing instances of the browser
    if browser_type == "firefox":
        webbrowser.get('firefox').open(url)
    elif browser_type == "chrome":
        webbrowser.get('chrome').open(url)
    elif browser_type == "brave":
        webbrowser.get('brave-browser').open(url)
    else:
        print(f"Browser type {browser_type} not supported.")
        return
    # Wait for the browser to likely be open)
    time.sleep(2)
    pyautogui.press('f11')
    #time.sleep(2)
    #pyautogui.press('k')

def clean_string(input_string):
    """Remove special characters, spaces, and make the string case insensitive."""
    # Remove special characters and spaces, then convert to lowercase
    cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', input_string).lower()
    # Return only the first 20 characters
    return cleaned_string[:20]

def rename_latest_html_file(directory, search_string, insight_id, subject_id, search_id):
    # Prepare the cleaned search string
    cleaned_search_string = clean_string(search_string)
    print(f'cleaned_search_string: {cleaned_search_string}')

    # Prepare the search pattern for .html files
    search_pattern = os.path.join(directory, '**', '*.html')
    print(f'search_pattern: {directory}')
    # List all HTML files in the directory and subdirectories
    files = glob.glob(search_pattern, recursive=True)

    # Filter files by checking the cleaned file name against the cleaned search string
    matching_files = []
    for file in files:
        # Get just the file name without the path
        filename = os.path.basename(file)
        print(f'checking {filename} for {cleaned_search_string}')
        
        # Clean the file name
        cleaned_filename = clean_string(filename)
        
        # Check if the cleaned search string is in the cleaned file name
        if cleaned_search_string in cleaned_filename:
            # Add file and its modification time to the list
            matching_files.append((file, os.path.getmtime(file)))
            print(f'Found matching file: {filename}')

    # Check if there are matching files
    if not matching_files:
        print("No matching HTML files found.")
        return

    # Sort files by modification time, get the latest one
    latest_file = max(matching_files, key=lambda x: x[1])[0]

    # Generate new file name
    new_file_name = f"{insight_id}_{subject_id}_{search_id}_{os.path.basename(latest_file)}"

    # New file path
    new_file_path = os.path.join(os.path.dirname(latest_file), new_file_name)

    # Rename the file
    os.rename(latest_file, new_file_path)
    print(f"Renamed file to: {new_file_path}")

def write_search_terms_to_json(search_terms, output_filename):
    print(f'writing to file: {output_filename}')
    with open(output_filename, 'w') as file:
        json.dump(search_terms, file, indent=4)  # Use indent for pretty printing
    return output_filename

def read_search_terms_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def main():
    # Retrieve search terms from the database
    search_terms = fetch_data(sql_query)

    write_search_terms_to_json(search_terms, output_filename)
    time.sleep(30)
    # Now read the terms back from the file
    input_filename = get_latest_json_file(directory)
    print(f'input_filename: {input_filename}')
    search_terms = read_search_terms_from_json(input_filename)

    open_url(url, browser_type)
    # Check the structure of the first element (if exists)
    if search_terms:
        print(f"Structure of the first search term: {search_terms[0]}")
    
    # Generate and execute commands for each unique search URL
    # Assuming each dictionary has a key 'search_term' that holds the actual term.
    for term_dict in search_terms:
        if 'search_term' in term_dict:
            search_term = term_dict['search_term']
            print(f'search_term: {search_term}')
            insight_id = term_dict['insight_id']
            subject_id = term_dict['subject_id']
            search_id = term_dict['search_id']
            print(f'subject_id: {search_term} search_id: {search_id}')
            #time.sleep(10)
            #search_url = generate_search_url(search_term)  # Pass only the search term string
            #print(f'search_term: {search_url}')  # Optional: print URL to console for tracking
            #open_url(search_url, browser_type)

            type_commands(search_term)
            time.sleep(2)
            rename_latest_html_file(dl_directory, search_term, insight_id, subject_id, search_id)
        else:
            print("Warning: 'search_term' key not found in the term dictionary.")
        time.sleep(random.randint(3, 6))  # Random wait between URLs

if __name__ == "__main__":
    main()
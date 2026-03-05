"""
BKDS LLM Base Prompt and Enrichment Processor

This script is designed to process JSON files containing data for LLM (Large Language Model) base prompt generation and enrichment. 
It iterates through files in a specified directory, matching an optional pattern, and applies a sequence of processing steps:
LLM base prompt generation, content enrichment, and final LLM processing. The script is tailored to handle structured data 
from JSON files, generate prompts based on this data, enrich them, and process them through an LLM.

Features:
- Processes JSON files in a specified directory, matching an optional file pattern.
- Generates LLM base prompts, enriches them, and processes them through an LLM.
- Logs activities for each processing step, aiding in tracking and debugging.

Usage:
- Execute the script with a directory path to JSON files: `python [script_name.py] <path_to_json_files>`
- Optionally, specify a pattern to match specific JSON files: `python [script_name.py] <path_to_json_files> --pattern <file_pattern>`

Dependencies:
- Requires Python modules: `argparse`, `json`, `glob`, `os`.
- Custom functions/modules: `process_llm_data`, `process_llm_prompt`, `llm_process`, and logging utilities.

Example:
To process all JSON files in the directory '/data/llm_prompts':
    `python [script_name.py] /data/llm_prompts`

To process only files matching the pattern '*_prompt.json' in the same directory:
    `python [script_name.py] /data/llm_prompts --pattern *_prompt.json`
"""

import argparse
import os
import json
import time
from datetime import datetime

#custom functions
from bkdsUtilities import log_msg, fetch_data, subjGenOutputHandler, getHash, db_load_llm_chat, get_sqlTemplate
from bkds_llmSubjEnrich import llm_handle_prompts
#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
query_key = 'bkds_llmPromptjGen_source'
sql_query=get_sqlTemplate(query_key)

# Assuming 'BKDS_NODEJS_DATA' is an environment variable set to a directory path
out_path = os.environ.get('BKDS_UTIL_DATA')
print('bkds_subj_path', out_path)

out_folder='llm_subjGen'
out_file_prefix='bkds_'
out_dir=os.path.join(out_path, f'output/subjGen/{out_folder}')
print(f'out_dir: {out_dir}')
out_type='json'
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
target_schema='dev'
target_obj='llm_processed_contents'
target_table=f'{target_schema}.{target_obj}'

batch_id='BKDS_LLM_SUBJ_PROCESS'
######################################################################
# Main logic and functions  
# Function to log messages
def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def replace_placeholders(template, row_data):
    """
    Recursively replace placeholders in the template and in row_data values.

    :param template: The template string with placeholders.
    :param row_data: A dictionary representing a row of data with keys and values.
    :return: The template string with placeholders replaced by actual values.
    """

    def replace_in_string(s, data):
        for k, v in data.items():
            placeholder = f"@@_{k}_@@"
            s = s.replace(placeholder, str(v))
        return s

    def recursive_replace(data):
        if isinstance(data, dict):
            return {k: recursive_replace(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [recursive_replace(item) for item in data]
        elif isinstance(data, str):
            return replace_in_string(data, row_data)
        else:
            return data

    # Replace placeholders in row_data values first
    row_data = recursive_replace(row_data)

    # Then replace placeholders in the template
    return replace_in_string(template, row_data)


def setup_prompt(raw_prompt):
    """
    Process the raw_prompt and return them as a JSON string, with each message in llm_messages
    wrapped in metadata including url_id, prompt_id, and persona_id.

    :param raw_prompt: The raw_prompt from fetch_data.
    :return: A JSON string representing the processed raw_prompt.
    """
    prompt_data = []

    if raw_prompt:
        # Process and append the global message only once
        first_row = raw_prompt[0]
        llm_global_prompt = replace_placeholders(first_row.get('prompt_template_system', ''), first_row)
        logMsg(f'llm_global_prompt: {llm_global_prompt}')
        time.sleep(20)
        global_message = {"role": "system", "content": llm_global_prompt}
        prompt_data.append(global_message)

        for row in raw_prompt:
            #print(f'llm_subj_prompt before: {row}')
            llm_subj_prompt = replace_placeholders(row.get('prompt_template_user', ''), row)
            #print(f'llm_subj_prompt after: {llm_subj_prompt}')
            # Metadata for each user message
            metadata = {
                "url_id": row.get('url_id', ''),
                "prompt_id": row.get('prompt_id', ''),
                "persona_id": row.get('persona_id', ''),
                "page_url": row.get('page_url', '')
            }
            

            # Wrapping each user message with metadata
            subj_prompt = {**metadata, "role": "user", "content": llm_subj_prompt}
            
            # Adding wrapped user messages to prompt_data
            prompt_data.append(subj_prompt)

        return json.dumps(prompt_data, indent=4)
    
    return None

def writeFile(data):
    content_hash=getHash(data)
    return subjGenOutputHandler(data, out_folder, out_file_prefix, out_type, program_name, content_hash)

def main():
    logMsg(f"{program_name} begins...")

    # Ensure output directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    raw_prompt = fetch_data(sql_query)

    if raw_prompt:
        llm_prompt = setup_prompt(raw_prompt)
        logMsg(f'llm_prompt: {llm_prompt}')
        llm_results = llm_handle_prompts(llm_prompt)
        out_file = writeFile(llm_results)
        logMsg(f'wrote output to: {out_file}')
        #load_table_from_file(out_file, target_table)
        db_load_llm_chat(out_file, target_table)

    logMsg(f"{program_name} ends...")

if __name__ == "__main__":
    main()

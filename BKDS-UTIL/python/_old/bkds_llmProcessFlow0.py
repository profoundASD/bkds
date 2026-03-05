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
- Custom functions/modules: `process_llm_data`, `process_llm_prompt`, `llm_enrich`, and logging utilities.

Example:
To process all JSON files in the directory '/data/llm_prompts':
    `python [script_name.py] /data/llm_prompts`

To process only files matching the pattern '*_prompt.json' in the same directory:
    `python [script_name.py] /data/llm_prompts --pattern *_prompt.json`
"""

import argparse
import os
import sys
from bkds_llmSubjEnrich import llm_enrich
from bkdsUtilities import log_msg, fetch_data
import time
import json
from datetime import datetime
#####################################################################
# Main Setup / Variables

def parse_arguments():
    parser = argparse.ArgumentParser(description="BKDS LLM Base Prompt and Enrichment Processor")
    parser.add_argument("sql_query", help="SQL query to fetch data from the database")
    return parser.parse_args()

args = parse_arguments()
sql_query = args.sql_query
# Database query processing logic here

# Assuming 'BKDS_NODEJS_DATA' is an environment variable set to a directory path
out_path = os.environ.get('BKDS_NODEJS_DATA')
print('bkds_subj_path', out_path)

out_folder='llm_enriched_subjects'
out_file_prefix='bkds_llm_enriched_'
out_dir=os.path.join(out_path, f'output/subjGen/{out_folder}')
print(f'out_dir: {out_dir}')
out_type='json'

wait_interval=10
######################################################################
# Main logic and functions  
# Function to log messages
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_PROCESS_SUBJ_CONTENT', msg)
    print(msg)

def llm_enrich(llm_global_prompt, llm_subj_prompt):
    """
    Enrich the provided text using a language model and return the results as a JSON string.

    :param text_chunk: The text to be enriched.
    :param prompt_id: The identifier for the prompt.
    :param insight_id: The identifier for the insight.
    :return: JSON string containing llm_reply, messages, and insight_id.
    """
    messages = [{"role": "system", "content": f"{llm_global_prompt}"}]
    logMsg(f'llm_enrich starting with messages: {messages}')

    if llm_subj_prompt:
        append_message(messages, "user", llm_subj_prompt)
        llm_reply = get_chat_reply(messages)
        if llm_reply:
            append_message(messages, "assistant", llm_reply)
            # Pack data into a JSON string and return
            output_data = {
                "llm_reply": llm_reply,
                 "messages": messages
            }
            logMsg(f'llm_reply complete, returning data')
            return json.dumps(output_data)
        else:
            logMsg("Failed to get a chat llm_reply.")
            return json.dumps({"error": "Failed to get llm_reply"})
    else:
        logMsg("No text chunk provided for enrichment.")
        return json.dumps({"error": "No text chunk provided"})
    
def main():
    logMsg("LLM process flow main...")

    # Ensure output directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    llm_prompt = None
    results = fetch_data(sql_query)
    if results:
        i = 0
        for row in results:
            print(f'row result# {i} of {sql_query}')
            llm_global_prompt = row.get('prompt_template_system', '')

            for key in row:
                placeholder = f"@@_{key}_@@"
                if placeholder in llm_global_prompt:
                    llm_global_prompt = llm_global_prompt.replace(placeholder, str(row[key]))

            llm_subj_prompt = row.get('prompt_template_user', '')
            for key in row:
                placeholder = f"@@_{key}_@@"
                if placeholder in llm_subj_prompt:
                    llm_subj_prompt = llm_subj_prompt.replace(placeholder, str(row[key]))

            enriched_content_str = llm_enrich(llm_global_prompt, llm_subj_prompt)
            insight_id = row.get('insight_id', '')
            prompt_id = row.get('prompt_id', '')
            print(f'insight_id: {insight_id}, prompt_id: {prompt_id}')
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            program_name = os.path.basename(__file__)

            # Convert string to dictionary
            try:
                enriched_content = json.loads(enriched_content_str)
            except json.JSONDecodeError:
                logMsg("Error decoding JSON from enriched content")
                continue

            # Add additional data to enriched_content
            enriched_content['insight_id'] = insight_id
            enriched_content['prompt_id'] = prompt_id
            enriched_content['timestamp'] = timestamp
            enriched_content['program_name'] = program_name

            output_file = os.path.join(out_dir, f'{out_file_prefix}_{insight_id}_{prompt_id}_{timestamp}.{out_type}')
            logMsg(f'writing to {output_file}')

            # Write the enriched content to a file in JSON format
            with open(output_file, 'w') as file:
                json.dump(enriched_content, file, indent=4)

            i += 1
            time.sleep(wait_interval)

if __name__ == "__main__":
    main()

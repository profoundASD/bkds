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
from bkdsUtilities import log_msg, fetch_data, subjGenOutputHandler
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
out_file_prefix='bkds_'
out_dir=os.path.join(out_path, f'output/subjGen/{out_folder}')
print(f'out_dir: {out_dir}')
out_type='json'
######################################################################
# Main logic and functions  
# Function to log messages
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_PROCESS_SUBJ_CONTENT', msg)
    print(msg)

def replace_placeholders(template, row_data):
    """
    Replace placeholders in the template with corresponding values from the row data.

    :param template: The template string with placeholders.
    :param row_data: A dictionary representing a row of data with keys and values.
    :return: The template string with placeholders replaced by actual values.
    """
    for key, value in row_data.items():
        placeholder = f"@@_{key}_@@"
        template = template.replace(placeholder, str(value))
    return template

def main():
    logMsg("LLM process flow main...")

    # Ensure output directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    results = fetch_data(sql_query)
    if results:
        # Apply the replacement logic to the global prompt
        llm_global_prompt=[]
        llm_global_prompt = replace_placeholders(results[0].get('prompt_template_system', ''), results[0])
        llm_subj_prompt = []
        # Prepare all subject prompts with associated IDs        
     
        for row in results:
            llm_subj_prompt = replace_placeholders(row.get('prompt_template_user', ''), row)
            insight_id = row.get('insight_id', '')
            prompt_id = row.get('prompt_id', '')
            persona_id = row.get('persona_id', '')

            logMsg(f'\llm_global_prompt\n\n {llm_global_prompt}')

            enriched_contents = llm_enrich(llm_global_prompt, llm_subj_prompt)
            #enriched_contents=[]
            logMsg(f'enriched_contents: {enriched_contents}\n\n')
            # Process and write each enriched content
            for enriched_content in enriched_contents:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                program_name = os.path.basename(__file__)

                # Add additional data to enriched_content
                enriched_content.update({
                    'timestamp': timestamp,
                    'program_name': program_name,
                    'insight_id':insight_id,
                    'prompt_id':prompt_id,
                    'persona_id':persona_id
                })

                output_filepath = subjGenOutputHandler(enriched_content, out_folder, out_file_prefix, out_type, insight_id, str(prompt_id) + '_' + str(persona_id), timestamp)
                logMsg(f'writing to {output_filepath}')

        logMsg(f'output_filepath {output_filepath}')
if __name__ == "__main__":
    main()

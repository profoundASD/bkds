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
import glob
import json
import os
import sys
from bkds_llmBasePromptGen import process_llm_data
from bkds_subjGenEnrichContent import process_llm_prompt
#from bkds_subjLLMEnrich import llm_enrich
from bkdsUtilities import log_msg, fetch_data

#####################################################################
# Main Setup / Variables

def parse_arguments():
    parser = argparse.ArgumentParser(description="BKDS LLM Base Prompt and Enrichment Processor")
    parser.add_argument("path", help="Path to the directory containing JSON files")
    parser.add_argument("pattern", help="Path to the directory containing JSON files")
    return parser.parse_args()

args = parse_arguments()
data_dir = args.path
file_pattern = args.pattern

src_data = 'v_llm_api_prompt_source'
src_schema = 'dev'
load_table = 'stg_llm_bkds_enriched_insights'
load_schema = 'dev'  # Modify if needed
sql_query = f"""
                SELECT 
                --## prompt/llm section ##
                prompt_id
                ,prompt_key
                --llm role
                ,llm_role
                ,llm_expertise
                ,llm_goal
                ,llm_goal_desc
                --prompt detail
                ,prompt_type
                ,prompt_intro
                ,prompt_description
                ,data_output_profile
                ,data_source_1
                ,key_concepts
                --## llm audience section ##
                ,persona_id
                ,occupation
                ,interests
                ,audiencedesc
                --custom audience traits/attributes
                ,trait1
                ,trait2
                ,trait3
                ,trait4
                ,trait5
                ,insight_id
                --source prompt content to transform
                ,search_term
                ,subj_title
                ,category
                ,page_url
                ,text_chunk
                FROM {src_schema}.{src_data}
              """

textGenScript='bkds_subjGenTextContent.py'
batch_id='helloworld1234'
# Database setup
db_params = {
    "host": "localhost",
    "database": "bkds",
    "user": "bkdsdev",
    "password": "hello"
}

# Assuming 'BKDS_NODEJS_DATA' is an environment variable set to a directory path
bkds_subj_path = os.environ.get('BKDS_NODEJS_DATA')
print('bkds_subj_path', bkds_subj_path)
print('data_dir', data_dir)
json_file_path = os.path.join(bkds_subj_path, data_dir)  # Define json_file_path here
print('bkds_subj_path', bkds_subj_path)
print('json_file_path', json_file_path)

######################################################################
# Main logic and functions
# Function to log messages
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_PROCESS_SUBJ_CONTENT', msg)
    print(msg)

def process_file(data_row):
    #logMsg(f"process_file : {data_row}")
    # Extracting necessary data for enrichment
    insight_id = data_row["insight_id"]

    # LLM Base Prompt Generation
    # bkds_llmBasePromptGen
    #llm_prompt = process_llm_data(data_row, insight_id)
    #logMsg(f"Generated LLM Prompt: {llm_prompt}")
    
    llm_prompt_data = data_row['transformed_prompt']
   # print(f'using llm_prompt_data: {llm_prompt_data}')

    if llm_prompt_data and isinstance(llm_prompt_data, list):
        prompt_id = llm_prompt_data[0].get("prompt_id")
    else:
        prompt_id = None 

    logMsg(f"insight_id: {insight_id}")
    logMsg(f"prompt_id: {prompt_id}")

    # Enrichment of Content
    #bkds_subjGenEnrichContent
    enriched_content = process_llm_prompt(insight_id, prompt_id, llm_prompt_data)
    logMsg(f"Enriched_Content: {enriched_content}")

    # Final LLM Processing
#  final_result = llm_enrich(enriched_content, insight_id)
#  logMsg(f"Final LLM Result: {final_result}")

def main():
    logMsg(f"llm process flow main...")
    # Construct the full path for file pattern matching
    full_path_pattern = os.path.join(json_file_path, file_pattern)
    logMsg(f'using: {full_path_pattern}')
    # Process each file that matches the pattern
    for file_name in glob.glob(full_path_pattern):
        with open(file_name, 'r') as file:
            logMsg(f'found file_name: {file_name}')
            data_row = json.load(file)
            process_file(data_row)

if __name__ == "__main__":
    main()

"""
BKDS LLM Base Prompt Generator

This script fetches data from the BKDS database and builds a structured JSON output. It can be filtered by prompt ID and insight ID, and uses a batch ID for logging purposes.

The script handles connection to a PostgreSQL database, executes a predefined query, and transforms the result set into a JSON structure.

Arguments:
- prompt_id (optional): ID of the prompt to query in the database.
- insight_id (optional): ID of the insight to query in the database.
- batch_id: Batch ID for logging purposes.

Usage:
python bkds_llmBasePromptGen.py --batch_id <batch_id> [--prompt_id <prompt_id>] [--insight_id <insight_id>]

Author: [Your Name]
Version: 1.0
Last Updated: [Date]
"""

import psycopg2
import json
import argparse
import os
import sys
from datetime import datetime
from bkdsUtilities import log_msg, subjGenOutputHandler
from bkds_subjGenEnrichContent import process_llm_prompt 
#####################################################################
# Main Setup / Variables

subjType='llm_wiki_prompts'
output_prefix='bkds_llmBasePrompt'
output_type='json'
batch_id=sys.argv[0]
full_program_name = sys.argv[0]
batch_id = os.path.basename(full_program_name)
########################################################################
#  Main logic and functions
    
# Logging Function
def logMsg(msg):
    log_msg(os.path.basename(__file__), batch_id, msg)
    print(msg)

# Function to replace placeholders with actual data
def apply_template(data_row, prompt_template):
    # Initialize transformed_prompt with the initial template
    transformed_prompt = prompt_template
    print(f'data_row.items() {data_row.items()}')

    if prompt_template:
        for key, value in data_row.items():
            # Create the placeholder pattern for the current key
            placeholder = f"@@_{key}_@@"

            # Replace the placeholder in the template with the actual value
            # Here, transformed_prompt is updated in each iteration
            transformed_prompt = transformed_prompt.replace(placeholder, str(value))

    return transformed_prompt


def construct_llm_prompt(data_row):
    logMsg(f'construct_llm_prompt: {type(data_row)}')
   # print(f'construct_llm_prompt {data_row}')

    # Check if prompt_template is in data_row
    prompt_template = data_row.get('prompt_template')  # If it's supposed to be directly in data_row
    #print('construct_llm_prompt project_template', data_row)
    return data_row.get('prompt_id'), data_row.get('insight_id'), json.dumps(apply_template(data_row, prompt_template))

# Main Execution (Updated)
def gen_llm_prompt(data, insight_id):
    logMsg("Starting BKDS LLM Base Prompt Generator")
    print(f'process_llm_data insight_id: {type(insight_id)}')

    results = []

    if data:
        # Process the single row represented by 'data'
        prompt_id, new_insight_id, transformed_prompt = construct_llm_prompt(data)
        logMsg(f"Prompt ID: {prompt_id}, Transformed Prompt: \n{transformed_prompt}")

        # Construct output_data based on the returned values
        output_data = {
            "transformed_prompt": transformed_prompt,
            "batch_id": batch_id,  # Ensure batch_id is defined or passed to this function
            "insight_id": new_insight_id,
            "prompt_id": prompt_id
        }
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        if output_data:
            output_filepath = subjGenOutputHandler(output_data, subjType, output_prefix, output_type, batch_id, insight_id, timestamp)
            logMsg(f'output: {output_filepath}')
            results.append(output_data)
        else:
            logMsg(f"Failed to get a chat llm_reply for insight_id: {insight_id}.")
            results.append({"insight_id": insight_id, "error": "Failed to get llm_reply"})
    else:
        logMsg("No data fetched")
        return json.dumps({"error": "No data fetched"})

    return json.dumps(results)
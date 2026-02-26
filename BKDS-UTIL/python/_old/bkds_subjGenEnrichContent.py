"""
BKDS Subject Generation and Enrichment Process

This script is designed for the automated extraction, enrichment, and storage of textual insights.
It fetches text data (insights) from a specified PostgreSQL view, enriches this text using the 
OpenAI language model through the `llm_enrich` function, and then loads the enriched results 
into a PostgreSQL database for further analysis and use.

Workflow:
1. Fetch data: Retrieves `insight_id` and `llm_prompt` from the `v_bkds_subjGen_source` view in the `dev` schema.
2. Enrich text: Each text chunk is processed with `llm_enrich` which interfaces with OpenAI's language model to generate enriched content.
3. Load results: Enriched insights are stored in the `stg_llm_bkds_enriched_insights` table within the `dev` schema. 

Each record includes metadata such as a unique load identifier, the timestamp of the load, and the name of this loading process.

"""
import os
import sys
from bkdsUtilities import log_msg
from bkds_llmSubjEnrich import llm_enrich

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
wait_period=3 #seconds
######################################################################
# Main logic and functions
# Function to log messages
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_PROCESS_SUBJ_CONTENT', msg)
    print(msg)



# Function to process llm_prompt with bkds_subjGenTextContent.py
def process_llm_prompt(insight_id, prompt_id, llm_prompt):
    logMsg(f'process_llm_prompt: {insight_id}')
    try:
        # Call the function directly
        results =llm_enrich(llm_prompt, prompt_id, insight_id)
        return results
       # load_insight_results(results)
        #return 0  # Assuming process_text does not return but raises exceptions on failures
    except Exception as e:  # Catch a more general exception if process_text can raise other types of exceptions
        logMsg(f"Error processing program: {program_name} subject: {insight_id} prompt: {prompt_id}: {e}")
        return 1  # Non-zero return code for error


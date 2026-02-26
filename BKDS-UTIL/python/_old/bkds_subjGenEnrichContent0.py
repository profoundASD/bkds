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
import psycopg2
import uuid
import sys
import json
import time
import datetime
from bkdsUtilities import log_msg, fetch_data
from bkds_subjLLMEnrich import llm_enrich

#####################################################################
# Main Setup / Variables
program_name = os.path.basename(__file__)
src_data = 'v_bkds_subjgen_source'
src_schema = 'dev'
load_table = 'stg_llm_bkds_enriched_insights'
load_schema = 'dev'  # Modify if needed
sql_query = f"""
                SELECT insight_id, prompt_id, llm_prompt 
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
wait_period=3 #seconds
######################################################################
# Main logic and functions
# Function to log messages
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_PROCESS_SUBJ_CONTENT', msg)
    print(msg)


# Function to create or replace the load table
def create_or_replace_table():
    logMsg(f'create_or_replace_table')
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {load_schema}.{load_table} (
                    insight_id TEXT,
                    prompt_id TEXT,
                    llm_reply TEXT,
                    load_id UUID,
                    load_date TIMESTAMP,
                    load_process TEXT
                );
            """)
            conn.commit()
    logMsg("Table created/replaced successfully.")

# Function to load insight results to the database

def load_insight_results(result_json):
    logMsg(f'load_insight_results {load_schema}.{load_table} ')
    create_or_replace_table()

    # Check if result_json is a string and convert it to a dictionary
    if isinstance(result_json, str):
        try:
            result_json = json.loads(result_json)
        except json.JSONDecodeError as e:
            logMsg(f"Error decoding JSON: {e}")
            return

    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            insert_query = f"""
                INSERT INTO {load_schema}.{load_table} (insight_id, prompt_id, llm_reply, load_id, load_date, load_process)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            load_id = str(uuid.uuid4())
            load_date = datetime.datetime.now()
            try:
                cur.execute(insert_query, (result_json['insight_id'], result_json['prompt_id'], result_json['llm_reply'], load_id, load_date, program_name))
                conn.commit()
                logMsg(f"Insight loaded successfully: {result_json['insight_id']} andprompt ID {result_json['prompt_id']}")
            except Exception as e:
                logMsg(f"Error inserting data into database: {e}")


# Function to process llm_prompt with bkds_subjGenTextContent.py
def process_llm_prompt(insight_id, prompt_id, llm_prompt):
    logMsg(f'process_llm_prompt: {insight_id}')
    try:
        # Call the function directly
        results =llm_enrich(llm_prompt, prompt_id, insight_id)
        logMsg(f'process_llm_prompt_results {results}')
        load_insight_results(results)
        return results  # Assuming process_text does not return but raises exceptions on failures
    except Exception as e:  # Catch a more general exception if process_text can raise other types of exceptions
        logMsg(f"Error processing program: {program_name} subject: {insight_id} prompt: {prompt_id}: {e}")
        return 1  # Non-zero return code for error

def main():
    data = fetch_data(sql_query)
    #logMsg(f'fetched data {data}')
    for insight_id, prompt_id, llm_prompt in data:
        logMsg(f'fetched data for {insight_id} and {llm_prompt}')
        return_code = process_llm_prompt(insight_id, prompt_id, llm_prompt)
        if return_code == 0:
            logMsg(f"Successfully processed data for {insight_id} and {prompt_id}")
        else:
            logMsg(f"Failed to process insight_id {insight_id} and {prompt_id} with return code {return_code}")
        time.sleep(wait_period)

if __name__ == "__main__":
    main()

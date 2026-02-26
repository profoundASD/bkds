"""
OpenAI Language Model Enrichment and PostgreSQL Integration Script

This script is designed to enrich textual content using OpenAI's GPT-3.5 model and subsequently store the
enriched insights in a PostgreSQL database. It fetches text data identified by `insight_id` from a PostgreSQL view, 
processes each text chunk using OpenAI's language model to generate enriched responses, 
and then loads the results into a database table.

Key Features:
- Fetches `insight_id` and `text_chunk` from a PostgreSQL view (`v_bkds_subjGen_source`).
- Utilizes OpenAI's Chat Completion model (`gpt-3.5-turbo`) to enrich text chunks, generating context-aware responses.
- Stores the enriched content along with metadata (such as load ID and timestamp) in a PostgreSQL table (`stg_llm_bkds_enriched_insights`).
- Handles batch operations with a defined wait period, allowing for controlled processing of large datasets.

Dependencies:
- Requires the `openai` Python package for interacting with OpenAI's API.
- Utilizes `psycopg2` for PostgreSQL database interactions.
- Leverages custom utility functions from `bkdsUtilities` for logging.

Environment Variables:
- `OPENAI_API_KEY`: Required for authentication with OpenAI's API.
- `BKDS_NODEJS_DATA`: Path configuration for data processing.
- Database credentials are configured via `db_params`.
"""

import os
import json
import os
import sys
from bkdsUtilities import log_msg
import os
import json
# Set OpenAI API key
from openai import OpenAI
import requests
import time
#####################################################################
# Main Setup / Variables
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_SUBJ_CONTENT_GEN', msg)
    print(msg)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
logMsg(f"openaiClient env: {api_key}")

bkds_subj_path = os.environ.get('BKDS_NODEJS_DATA')
if not bkds_subj_path:
    raise EnvironmentError("BKDS_NODEJS_DATA environment variable is not set.")
logMsg(f"bkds_subj_path env: {bkds_subj_path}")

wait_interval=5
########################################################################
# Main logic and functions
def get_chat_reply(messages):
    logMsg(f'get_chat_reply function')
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code
        chat_response = response.json()
        #logMsg(f"chat_response['choices'][0]['message']['content']: {chat_response}")
        return chat_response
    except requests.exceptions.RequestException as e:
        logMsg(f"OpenAI Error: {str(e)}")
        return None

def append_message(messages, role, content):
    logMsg(f'append_message with role: {role}')
    """
    Append a message to the conversation history.

    :param messages: The conversation history.
    :param role: The role of the message sender ('user' or 'assistant').
    :param content: The message content.
    """
    messages.append({"role": role, "content": content})

def llm_enrich(llm_global_prompt, llm_subj_prompts_with_ids):
    """
    Enrich a list of text prompts using a language model and return the results.
    Sets the global prompt once and handles each assistant prompt.

    :param llm_global_prompt: The global prompt text.
    :param llm_subj_prompts_with_ids: List of tuples containing subject prompts and their associated IDs.
    :return: List of dictionaries containing llm_reply, messages, insight_id, and prompt_id.
    """
    messages = [{"role": "system", "content": llm_global_prompt}]
    logMsg(f'llm_enrich starting with messages: {messages}')
    results = []
    #print(f'llm_subj_prompts_with_ids {llm_subj_prompts_with_ids}')
    for subj_prompt, insight_id, prompt_id in llm_subj_prompts_with_ids:
        if subj_prompt:
            prompt_messages = messages.copy()
            append_message(prompt_messages, "user", subj_prompt)
            llm_reply = get_chat_reply(prompt_messages)
            if llm_reply:
                append_message(prompt_messages, "assistant", llm_reply)
                output_data = {"llm_chain": prompt_messages, "insight_id": insight_id, "prompt_id": prompt_id}
            else:
                output_data = {"error": "Failed to get llm_reply", "insight_id": insight_id, "prompt_id": prompt_id}
        else:
            output_data = {"error": "No text chunk provided", "insight_id": insight_id, "prompt_id": prompt_id}

        results.append(output_data)
        logMsg(f'llm_reply for a prompt complete.')
        time.sleep(wait_interval)

    return results


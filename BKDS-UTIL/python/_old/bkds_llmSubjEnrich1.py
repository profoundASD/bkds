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
import hashlib
from datetime import datetime
import requests
from bkdsUtilities import log_msg, getHash
import sys

# Set up logging
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_SUBJ_CONTENT_GEN', msg)
    print(msg)

# Environment setup
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
logMsg(f"openaiClient env: {api_key}")

bkds_subj_path = os.environ.get('BKDS_NODEJS_DATA')
if not bkds_subj_path:
    raise EnvironmentError("BKDS_NODEJS_DATA environment variable is not set.")
logMsg(f"bkds_subj_path env: {bkds_subj_path}")

# Main logic
def get_chat_reply(messages):
    logMsg('get_chat_reply function')

    # Extract the relevant message content
    api_message = next((msg for msg in messages if msg['role'] == 'user'), None)
    if not api_message:
        logMsg("No user message found.")
        return None

    # Prepare data for API request
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [api_message],  # Only send the required user message
        "temperature": 0.7
    }

    # Make the API request
    try:
        logMsg(f'messages: {api_message}')
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        chat_response = response.json()
        logMsg(f"chat_response['choices'][0]['message']['content']: {chat_response}")
        return chat_response
    except requests.exceptions.RequestException as e:
        logMsg(f"OpenAI Error: {str(e)}")
        return None



def append_message(messages, role, content, meta=None, timestamp=None):
    message = {"role": role, "content": content}
    if meta:
        message["msg_meta"] = meta
    if timestamp:
        message["llm_date"] = timestamp
    messages.append(message)



def extract_assistant_content(content):
    """Extracts data from assistant message content."""
    return {
        "id": content.get("id"),
        "object": content.get("object"),
        "created": content.get("created"),
        "model": content.get("model"),
        "role": content["choices"][0]["message"].get("role"),
        "content": content["choices"][0]["message"].get("content"),
        "finish_reason": content["choices"][0].get("finish_reason"),
        "prompt_tokens": content["usage"].get("prompt_tokens"),
        "completion_tokens": content["usage"].get("completion_tokens"),
        "total_tokens": content["usage"].get("total_tokens")
    }

def process_messages_to_summary(json_data):
    """Processes messages to create a summary with metadata and content."""
    results = []

    for message in json_data:
        if not message.get("msg_meta"):
            continue

        record = {key: message.get(key) for key in ["role", "llm_date"]}
        record.update({key: message["msg_meta"].get(key) for key in ["insight_id", "prompt_id", "persona_id"]})

        if message["role"] == "assistant" and isinstance(message["content"], dict):
            record.update(extract_assistant_content(message["content"]))
        else:
            record["content"] = message.get("content")

        record_hash = hashlib.md5(json.dumps(record, sort_keys=True).encode()).hexdigest()
        record["record_id"] = getHash(record_hash)
        results.append(record)

    return results

def llm_enrich(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    conversation, results, output_messages = [], [], []
    for message in json_data:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        msg_meta = {k: message.get(k, '') for k in ['insight_id', 'prompt_id', 'persona_id']}

        if message['role'] == 'system':
            if conversation:
                results.append({"llm_chain": output_messages, "llm_date": timestamp})
                conversation, output_messages = [], []
            append_message(conversation, message['role'], message)
            append_message(output_messages, message['role'], message, msg_meta, timestamp)

        elif message['role'] == 'user':
            append_message(conversation, 'user', message['content'])
            append_message(output_messages, 'user', message['content'], msg_meta, timestamp)

            llm_reply = get_chat_reply(conversation)
            if llm_reply:
                assistant_reply = llm_reply['choices'][0]['message']['content']
                append_message(conversation, 'assistant', assistant_reply)
                append_message(output_messages, 'assistant', llm_reply, msg_meta, timestamp)
            else:
                conversation.append({"error": "Failed to get llm_reply"})

    if conversation:
        results.append({"llm_chain": process_messages_to_summary(output_messages), "llm_date": timestamp})

    return results

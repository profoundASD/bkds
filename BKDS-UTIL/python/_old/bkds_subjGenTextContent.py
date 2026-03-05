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

#####################################################################
# Main Setup / Variables
def logMsg(msg):
    log_msg(os.path.basename(sys.argv[0]), 'BKDS_SUBJ_CONTENT_GEN', msg)
    print(msg)

# Set OpenAI API key
from openai import OpenAI
if os.getenv("OPENAI_API_KEY"):
    openaiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 
    api_key=os.getenv("OPENAI_API_KEY")
    logMsg(f"openaiClient env: {api_key}")
else:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")


bkds_subj_path = os.environ.get('BKDS_NODEJS_DATA')
if bkds_subj_path:
    logMsg(f"bkds_subj_path env: {bkds_subj_path}")
else:
    raise EnvironmentError("BKDS_NODEJS_DATA environment variable is not set.")

########################################################################
# Main logic and functions

def get_chat_reply(messages):
    logMsg(f'get_chat_reply function')
    """
    Generate a chat reply using OpenAI's Chat model.

    :param messages: The conversation history.
    :return: The reply from the chat model.
    """
    try:
        chat = openaiClient.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo" )
        return chat.choices[0].message.content
    except openaiClient.error.OpenAIError as e:
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

def llm_enrich(text_chunk, insight_id):
    """
    Enrich the provided text using a language model and return the results as a JSON string.

    :param text_chunk: The text to be enriched.
    :param insight_id: The identifier for the insight.
    :return: JSON string containing llm_reply, messages, and insight_id.
    """
    messages = [{"role": "system", "content": "Objective below: "}]

    if text_chunk is not None:
        append_message(messages, "user", text_chunk)
        logMsg(f'appended user_message {text_chunk}')

        llm_reply = get_chat_reply(messages)
        if llm_reply is not None:
            append_message(messages, "assistant", llm_reply)

            # Pack data into a JSON string and return
            output_data = {
                "insight_id": insight_id,
                "llm_reply": llm_reply,
                "messages": messages
            }

            logMsg(f'output_data: {output_data}')   

            return json.dumps(output_data)
        else:
            logMsg("Failed to get a chat llm_reply.")
            return json.dumps({"insight_id": insight_id, "error": "Failed to get llm_reply"})
    else:
        logMsg("No text chunk provided for enrichment.")
        return json.dumps({"insight_id": insight_id, "error": "No text chunk provided"})

import os
import sys
import json
import time
from datetime import datetime
from argparse import ArgumentParser
from bkds_Utilities import log_msg, fetch_data, get_sqlTemplate, getHash, load_and_resolve_config
import requests
import random

##################################
# BKDS LLM Base Prompt and Enrichment Processor
##################################
"""
BKDS LLM Base Prompt and Enrichment Processor

Purpose:
    This script handles LLM-based prompt processing and enrichment tasks, enabling streamlined interaction 
    with a large language model (LLM) API. It processes structured data, generates prompts, fetches LLM 
    responses, and outputs results in a structured format. Additionally, it supports metadata-driven 
    configurations and dynamic file handling for efficient processing.

Logical Flow:
    1. **Argument Parsing**: Collects runtime parameters including batch IDs and configuration file paths.
    2. **Configuration Loading**: Resolves configurations from JSON files, supporting reusable common settings.
    3. **Prompt Handling**: Processes input data to generate prompts, wraps metadata, and invokes the LLM API.
    4. **Response Processing**: Summarizes API responses, enriches metadata, and prepares results for output.
    5. **File Management**: Writes processed outputs to files with configurable paths and formats.
    6. **Error Handling**: Logs and gracefully handles errors during configuration loading, API calls, and file operations.

Usage:
    python bkds_llm_processor.py --batch_id_process <batch_id> --batch_id_api <batch_id> --config_path <config_file>

    - `--batch_id_process`: Identifies the process flow configuration in the JSON file.
    - `--batch_id_api`: Identifies the API configuration in the JSON file.
    - `--config_path`: Path to the JSON configuration file containing runtime settings.

Example:
    python bkds_llm_processor.py --batch_id_process BKDS_LLM_PROCESS_SUBJGEN_FLOW --batch_id_api BKDS_LLM_API_CONFIG --config_path /path/to/config.json

Prerequisites:
    - Set the `BKDS_UTIL_DATA` environment variable for base file handling.
    - The `bkds_Utilities` Python module must be accessible.
    - Ensure API credentials are properly configured as environment variables (`OPENAI_API_KEY`).

"""

# Program Identifiers
program_name = os.path.basename(__file__)

##################################
# Global variables and setup
def load_configuration(config_path):
    print(f'Config path: {config_path}')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

def parse_arguments():
    """Parse command-line arguments."""
    parser = ArgumentParser(description="BKDS LLM Process Flow")
    parser.add_argument("--batch_id_process", required=True, help="Batch ID for process flow")
    parser.add_argument("--batch_id_api", required=True, help="Batch ID for API configuration")
    parser.add_argument("--config_path", required=True, help="Path to the JSON configuration file")
    return parser.parse_args()

args = parse_arguments()
batch_id_process = args.batch_id_process
batch_id_api = args.batch_id_api
config_path = args.config_path

# JSON Key Constants
TIMESTAMP_FORMAT = "timestamp_format"
LLM_MODEL = "llm_model"
LLM_TEMP = "llm_temp"
LLM_DEFAULT_TEMP=0.7
LLM_ENDPOINT = "llm_endpoint"
LLM_CONTENT_TYPE = "llm_content_type"
DB_REF_KEYS = "db_ref_keys"
MAINT_KEYS = "maint_keys"
OUTPUT_REC_KEY = "output_rec_key"
SLEEP_MIN = "sleep_duration_min"
SLEEP_MAX = "sleep_duration_max"
ROLE = "role"
CONTENT = "content"
ASSISTANT = "assistant"
SYSTEM = "system"
USER = "user"
MSG_META = "msg_meta"
LLM_DATE = "llm_date"
CHOICES = "choices"
MESSAGE = "message"
MESSAGES = f"{MESSAGE}s"
TEMP = "temperature"
MODEL = "model"
USAGE = "usage"
RECORD_ID="record_id"
ID = "id"
OBJECT = "object"
CREATED = "created"
ERROR = "error"

FINISH_REASON="finish_reason"
PROMPT_TOKENS="prompt_tokens"
COMPLETION_TOKENS="completion_tokens"
TOTAL_TOKENS="total_tokens"
URL_ID="url_id"
PROMPT_ID="prompt_id"
PAGE_URL="page_url"
PERSONA_ID="persona_id"
PROMPT_TEMPLATE_USER='prompt_template_user'
PROMPT_TEMPLATE_SYSTEM='prompt_template_system'
SLEEP_DURATION='sleep_duration'

QUERY_KEY = "query_key"
OUT_FILE_PREFIX = "out_file_prefix"
OUT_TYPE = "out_type"
OUTPUT_SUBFOLDER = "output_subfolder"
PROCESS_SUBFOLDER = "process_subfolder"

# Default values
DEFAULT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_AUTHORIZATION = "Authorization"
OPENAI_API_KEY = "OPENAI_API_KEY"

DEFAULT_SLEEP_MIN=3
DEFAULT_SLEEP_MAX=9

DEFAULT_LLM_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_LLM_TYPE = "application/json"
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"
DEFAULT_QUERY_KEY = "bkds_llmHygiene_source"
DEFAULT_OUT_FILE_PREFIX = "bkds_llm"
DEFAULT_OUT_TYPE = "json"
DEFAULT_OUTPUT_SUBFOLDER = "output"
DEFAULT_PROCESS_SUBFOLDER = "llm_process"
LLM_ERROR = "Failed to get llm_responses"

time_unit='second'

PLACEHOLDER_TEMPLATE= "@@_{key}_@@"

OS_UTIL_ENV='BKDS_UTIL_DATA'
OS_DEFAULT_ENV='.'

# Utility Functions

def logMsg(msg, batch_id=batch_id_process):
    """Log messages with batch ID and program name."""
    log_msg(program_name, batch_id, msg)
    print(f"[{batch_id}] {msg}")

# Load configuration
try:
    # Load and resolve configuration for process flow
    config_process = load_and_resolve_config(config_key=batch_id_process, config_path=config_path)
    # Load and resolve configuration for API
    config_api = load_and_resolve_config(config_key=batch_id_api, config_path=config_path)


except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as e:
    logMsg(f"Failed to load configuration: {e}")
    sys.exit(1)


query_key = config_process.get(QUERY_KEY, DEFAULT_QUERY_KEY)
out_file_prefix = config_process.get(OUT_FILE_PREFIX, DEFAULT_OUT_FILE_PREFIX)
out_type = config_process.get(OUT_TYPE, DEFAULT_OUT_TYPE)
output_subfolder = config_process.get(OUTPUT_SUBFOLDER, DEFAULT_OUTPUT_SUBFOLDER)
process_subfolder = config_process.get(PROCESS_SUBFOLDER, DEFAULT_PROCESS_SUBFOLDER)

# Prepare output folder
out_path = os.environ.get(OS_UTIL_ENV, OS_DEFAULT_ENV )
out_folder = os.path.join(out_path, output_subfolder, process_subfolder)

##################################
# Main logic and functions

def get_active_model(config_process, config_api):
    """
    Determine the active model based on `model_vary` in process configuration.
    If `model_vary` is True, randomly select a model from the available ones.
    Otherwise, use the default model (llm_model_0).
    """
    model_vary = config_process.get("model_vary", False)
    default_model = config_api.get("llm_model_0", DEFAULT_LLM_MODEL)

    if model_vary:
        # Extract all keys starting with "llm_model_"
        available_models = [v for k, v in config_api.items() if k.startswith("llm_model_")]
        if not available_models:
            logMsg("No models available; defaulting to llm_model_0.")
            return default_model
        return random.choice(available_models)  # Randomly select one model
    return default_model  # Return the default model


def handle_chat(messages, api_key, config_api, active_model):
    """
    Send chat data to OpenAI API and handle responses.
    Now includes dynamically determined `active_model`.
    """
    timestamp_format = config_api.get(TIMESTAMP_FORMAT, DEFAULT_TIMESTAMP_FORMAT)
    llm_temp = config_api.get(LLM_TEMP, LLM_DEFAULT_TEMP)
    llm_endpoint = config_api.get(LLM_ENDPOINT, DEFAULT_LLM_URL)
    llm_content_type = config_api.get(LLM_CONTENT_TYPE, DEFAULT_LLM_TYPE)
    headers = {
        HEADER_CONTENT_TYPE: llm_content_type,
        HEADER_AUTHORIZATION: f"Bearer {api_key}"
    }
    
    logMsg(f'handle_chat with LLM Model: {active_model} Model Temp: {llm_temp}')
    data = {
        MODEL: active_model,
        MESSAGES: messages,
        TEMP: llm_temp
    }

    try:
        response = requests.post(llm_endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logMsg(f"{active_model} error: {str(e)}")
        return None


def llm_handle_prompts(json_data, batch_id, config_process, config_api):
    """
    Process prompts for LLM interactions.
    Dynamically determine the active model based on `model_vary`.
    """
    api_key = os.getenv(OPENAI_API_KEY)
    logMsg(f'llm_handle_prompts begins for batch_id={batch_id}')

    if not api_key:
        raise EnvironmentError(f"{OPENAI_API_KEY} environment variable is not set.")

    timestamp_format = config_process.get(TIMESTAMP_FORMAT, DEFAULT_TIMESTAMP_FORMAT)

    logMsg(f"PROCESS CONFIG: {json.dumps(config_process, indent=4)}")
    logMsg(f"API CONFIG: {json.dumps(config_api, indent=4)}")

    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            logMsg("Error decoding JSON data")
            return []

    messages = []
    results = []
    db_ref_keys = config_process.get(DB_REF_KEYS, [URL_ID, PROMPT_ID, PERSONA_ID, PAGE_URL])
    sleep_duration_min = config_process.get(SLEEP_MIN, DEFAULT_SLEEP_MIN)
    sleep_duration_max = config_process.get(SLEEP_MAX, DEFAULT_SLEEP_MAX)

    # Determine the active model
    active_model = get_active_model(config_process, config_api)

    for message in json_data:
        msg_meta = {key: message.get(key, '') for key in db_ref_keys}
        msg_content = message.get(CONTENT)
        msg_role = message.get(ROLE)

        if msg_role == SYSTEM:
            logMsg(f'LLM_ROLE: {msg_role}')
            messages = []
            results = []
            messages.append({ROLE: SYSTEM, CONTENT: msg_content})
            logMsg(f'MSG APPENDED BY ROLE: {msg_role}')
            timestamp = datetime.now().strftime(timestamp_format)
            results.append({ROLE: msg_role, CONTENT: msg_content, MSG_META: msg_meta, LLM_DATE: timestamp})
            logMsg(f'MSG APPENDED TO RESULT LOG BY ROLE: {msg_role}')
        elif msg_role == USER:
            logMsg(f'LLM_ROLE == {msg_role}')
            messages.append({ROLE: USER, CONTENT: msg_content})
            logMsg(f'MSG APPENDED BY ROLE: {msg_role}')
            timestamp = datetime.now().strftime(timestamp_format)
            results.append({ROLE: msg_role, CONTENT: msg_content, MSG_META: msg_meta, LLM_DATE: timestamp})
            logMsg(f'MSG APPENDED TO RESULT LOG BY ROLE: {msg_role}')
            llm_responses = handle_chat(messages, api_key, config_api, active_model)
            logMsg(f'LLM RESPONSE HANDLING BEGINS: {msg_role} @ {datetime.now().strftime(timestamp_format)}')

            if llm_responses and CHOICES in llm_responses and llm_responses[CHOICES]:
                # Extract the assistant's message content
                assistant_content = llm_responses[CHOICES][0][MESSAGE][CONTENT]
                # Append only the assistant's content (string) to messages
                messages.append({ROLE: ASSISTANT, CONTENT: assistant_content})
                timestamp = datetime.now().strftime(timestamp_format)
                # Store the full llm_responses in results for later processing
                results.append({
                    ROLE: ASSISTANT,
                    CONTENT: llm_responses,  # Store full API response here
                    MSG_META: msg_meta,
                    LLM_DATE: timestamp
                })
                logMsg(f'LLM RESPONSE APPENDED BY ROLE: {ASSISTANT} @ {timestamp}')
            else:
                messages.append({ERROR: LLM_ERROR})
            
            sleep_time = random.randint(sleep_duration_min, sleep_duration_max)
            logMsg(f"Pausing for {sleep_time} {time_unit}s...")
            time.sleep(sleep_time)

    logMsg(f'Returning summarized results')
    return summarize_results(results, config_process)


def summarize_results(json_data, config_process):
    """Summarize and structure results for output."""
    logMsg(f'summarize_results @ {datetime.now().strftime(config_process.get(TIMESTAMP_FORMAT, DEFAULT_TIMESTAMP_FORMAT))}')
    results = []
    db_ref_keys = config_process.get(DB_REF_KEYS, [URL_ID, PROMPT_ID, PERSONA_ID, PAGE_URL])
    maint_keys = config_process.get(MAINT_KEYS, [ROLE, LLM_DATE])
    output_rec_key = config_process.get(OUTPUT_REC_KEY, RECORD_ID)
    model_keys = [MODEL, ID, OBJECT, CREATED]
    message_keys = [ROLE, CONTENT]
    reason_keys = [FINISH_REASON]
    usage_keys = [PROMPT_TOKENS, COMPLETION_TOKENS, TOTAL_TOKENS]

    for message in json_data:
        if not message.get(MSG_META):
            continue

        record = {key: message.get(key) for key in maint_keys}
        record.update({key: message[MSG_META].get(key) for key in db_ref_keys})

        if message[ROLE] == ASSISTANT and isinstance(message[CONTENT], dict):
            content = message[CONTENT]
            content_base = content[CHOICES][0]
            content_msg = content_base[MESSAGE]
            content_usage = content.get(USAGE, {})
            result = {key: content.get(key) for key in model_keys}
            result.update({key: content_msg.get(key) for key in message_keys})
            result.update({key: content_base.get(key) for key in reason_keys})
            result.update({key: content_usage.get(key) for key in usage_keys})
            record.update(result)
        else:
            record[CONTENT] = message.get(CONTENT)

        record[output_rec_key] = getHash(record)
        results.append(record)
    return results

def replace_placeholders(template, row_data):
    """Recursively replace placeholders in the template and in row_data values."""
    def replace_in_string(s, data):
        for k, v in data.items():
            placeholder = PLACEHOLDER_TEMPLATE.format(key=k)  # Use the constant template
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

    row_data = recursive_replace(row_data)
    return replace_in_string(template, row_data)

def setup_prompt(raw_prompt, config):
    """
    Process the raw_prompt and return them as a JSON string,
    with each message in `llm_messages` wrapped in metadata.
    """
    prompt_data = []
    sleep_duration = config.get(SLEEP_DURATION, DEFAULT_SLEEP_MIN)

    if raw_prompt:
        first_row = raw_prompt[0]
        llm_global_prompt = replace_placeholders(
            first_row.get(PROMPT_TEMPLATE_SYSTEM, ''),
            first_row
        )
        logMsg(f"CURRENT_ROLE: {USER}\n\nGLOBAL_PROMPT:\n\n{llm_global_prompt}\n")
        time.sleep(sleep_duration)
        global_message = {ROLE: SYSTEM, CONTENT: llm_global_prompt}
        logMsg(f'CURRENT_ROLE: {USER} GLOBAL_MESSAGE: \n\n {global_message} \n')
        prompt_data.append(global_message)

        for row in raw_prompt:
            llm_subj_prompt = replace_placeholders(
                row.get(PROMPT_TEMPLATE_USER, ''),
                row
            )
            metadata = {
                URL_ID: row.get(URL_ID, ''),
                PROMPT_ID: row.get(PROMPT_ID, ''),
                PERSONA_ID: row.get(PERSONA_ID, ''),
                PAGE_URL: row.get(PAGE_URL, '')
            }
            subj_prompt = {**metadata, ROLE: USER, CONTENT: llm_subj_prompt}
            logMsg(f'CURRENT_ROLE: {USER}\nsubj_prompt:\n{subj_prompt}\n')
            prompt_data.append(subj_prompt)

        return json.dumps(prompt_data, indent=4)
    return None

def write_output_file(data, folder, prefix, file_type, batch_id, timestamp):
    """Write data to an output file."""
    file_path = os.path.join(folder, f"{prefix}_{batch_id}_{timestamp}.{file_type}")
    with open(file_path, 'w') as output_file:
        json.dump(data, output_file, indent=4)
    logMsg(f"Output file written to: {file_path}")
    return file_path

def main():
    logMsg("Starting BKDS LLM Process Flow", batch_id_process)

    os.makedirs(out_folder, exist_ok=True)
    # File timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Fetch data and process prompts
    try:
        sql_query = get_sqlTemplate(query_key)
        raw_prompt = fetch_data(sql_query)

        if not raw_prompt:
            logMsg("No data fetched for the query.", batch_id_process)
            sys.exit(0)

        llm_prompt = setup_prompt(raw_prompt, config_process)
        llm_results = llm_handle_prompts(llm_prompt, batch_id_process, config_process, config_api)

        write_output_file(llm_results, out_folder, out_file_prefix, out_type, batch_id_process, timestamp)
    except Exception as e:
        logMsg(f"Error during LLM processing: {e}", batch_id_process)
        sys.exit(1)

    logMsg("BKDS LLM Process Flow completed successfully.", batch_id_process)

##################################
# Entry Point
##################################

if __name__ == "__main__":
    main()
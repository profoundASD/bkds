"""
Program Header: OpenAI Chat Interaction Handler

This program processes interactions with OpenAI's chat model, dynamically loading configurations for handling API requests,
logging, and processing responses based on a specified configuration key.

Usage:
- Stand-alone execution:
    `python bkds_backend_llmSubjEnrich.py --batch_id <batch_id> --config_key <config_key> --config_path <config_file_path>`
- As an imported module:
    Import functions and call them with explicit arguments.
"""

import os
import json
import sys
import time
import random
import requests
from datetime import datetime
from argparse import ArgumentParser
from bkds_Utilities import log_msg, getHash, getFunctionName
program_name = os.path.basename(__file__)

#####################################################################
# Argument Parsing

def parse_arguments():
    parser = ArgumentParser(description="OpenAI Chat Interaction Handler")
    parser.add_argument("--batch_id", required=True, help="Batch ID for processing")
    parser.add_argument("--config_key", required=True, help="Configuration key in the JSON config file")
    parser.add_argument("--config_path", required=True, help="Path to the JSON configuration file")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
config_key = args.config_key
config_path = args.config_path

#####################################################################
# Global Variables and

#####################################################################
# Load Configuration

def load_configuration(config_path, config_key):
    print(f'Config path: {config_path}')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)

    if config_key not in config_data:
        raise KeyError(f"Configuration key '{config_key}' not found in the configuration file")

    return config_data[config_key]

#####################################################################
# Main Logic and Functions

def logMsg(msg, batch_id, program_name):
    """Log messages with batch ID and program name."""
    log_msg(program_name, batch_id, msg)
    print(msg)

def handle_chat(messages, api_key, config):
    timestamp_format = config.get("timestamp_format", "%Y%m%d_%H%M%S")
    llm_model = config.get("llm_model", "gpt-4")
    llm_temp = config.get("llm_temp", 0.7)
    llm_endpoint = config.get("llm_endpoint", "https://api.openai.com/v1/chat/completions")
    llm_content_type = config.get("llm_content_type", "application/json")
    headers = {
        "Content-Type": llm_content_type,
        "Authorization": f"Bearer {api_key}"
    }
    logMsg(f'handle_chat @ {datetime.now().strftime(timestamp_format)}', batch_id, program_name)
    data = {
        "model": llm_model,
        "messages": messages,
        "temperature": llm_temp
    }
    try:
        response = requests.post(llm_endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logMsg(f"{llm_model} error: {str(e)}", batch_id, program_name)
        return None

def llm_handle_prompts(json_data, batch_id, config):
    program_name = os.path.basename(sys.argv[0])
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

    timestamp_format = "%Y%m%d_%H%M%S"
    logMsg(f'llm_handle_prompts begins for batch_id={batch_id}, config_key={config_key} @ {datetime.now().strftime(timestamp_format)}', batch_id, program_name)
    
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            logMsg("Error decoding JSON data", batch_id, program_name)
            return []

    messages = []
    results = []
    db_ref_keys = config.get("db_ref_keys", ["url_id", "prompt_id", "persona_id", "page_url"])
    maint_keys = config.get("maint_keys", ["role", "llm_date"])
    sleep_duration_min = config.get("sleep_duration_min", 3)
    sleep_duration_max = config.get("sleep_duration_max", 9)
    error_key = "error"
    error_message = "Failed to get llm_responses"

    for message in json_data:
        msg_meta = {key: message.get(key, '') for key in db_ref_keys}
        msg_content = message.get("content")
        msg_role = message.get("role")

        if msg_role == 'system':
            logMsg(f'Meta {msg_role}', batch_id, program_name)
            messages = []
            results = []
            messages.append({"role": 'system', "content": msg_content})
            timestamp = datetime.now().strftime(timestamp_format)
            results.append({"role": msg_role, "content": msg_content, "msg_meta": msg_meta, "llm_date": timestamp})
        elif msg_role == 'user':
            logMsg(f'{msg_role} == user', batch_id, program_name)
            messages.append({"role": 'user', "content": msg_content})
            timestamp = datetime.now().strftime(timestamp_format)
            results.append({"role": msg_role, "content": msg_content, "msg_meta": msg_meta, "llm_date": timestamp})

            llm_responses = handle_chat(messages, api_key, config)
            if llm_responses:
                llm_content = llm_responses["choices"][0]["message"]["content"]
                messages.append({"role": 'assistant', "content": llm_content})
                timestamp = datetime.now().strftime(timestamp_format)
                results.append({"role": 'assistant', "content": llm_responses, "msg_meta": msg_meta, "llm_date": timestamp})
            else:
                messages.append({error_key: error_message})

            sleep_time = random.randint(sleep_duration_min, sleep_duration_max)
            logMsg(f"Pausing for {sleep_time} seconds...", batch_id, program_name)
            time.sleep(sleep_time)

    logMsg(f'{getFunctionName()} returning summarized results', batch_id, program_name)
    return summarize_results(results, config, batch_id, program_name)

def summarize_results(json_data, config, batch_id, program_name):
    logMsg(f'summarize_results @ {datetime.now().strftime(config.get("timestamp_format", "%Y%m%d_%H%M%S"))}', batch_id, program_name)
    results = []
    db_ref_keys = config.get("db_ref_keys", ["url_id", "prompt_id", "persona_id", "page_url"])
    maint_keys = config.get("maint_keys", ["role", "llm_date"])
    output_rec_key = config.get("output_rec_key", "record_id")
    model_keys = ["id", "object", "created", "model"]
    message_keys = ["role", "content"]
    reason_keys = ["finish_reason"]
    usage_keys = ["prompt_tokens", "completion_tokens", "total_tokens"]

    for message in json_data:
        if not message.get("msg_meta"):
            continue

        record = {key: message.get(key) for key in maint_keys}
        record.update({key: message["msg_meta"].get(key) for key in db_ref_keys})

        if message["role"] == 'assistant' and isinstance(message["content"], dict):
            content = message["content"]
            content_base = content["choices"][0]
            content_msg = content_base["message"]
            content_usage = content.get("usage", {})
            result = {key: content.get(key) for key in model_keys}
            result.update({key: content_msg.get(key) for key in message_keys})
            result.update({key: content_base.get(key) for key in reason_keys})
            result.update({key: content_usage.get(key) for key in usage_keys})
            record.update(result)
        else:
            record["content"] = message.get("content")

        record[output_rec_key] = getHash(record)
        results.append(record)

    return results

def main():

    config = load_configuration(config_path, config_key)
    # Sample json_data for demonstration purposes
    json_data = []  # Replace with actual data loading logic

    results = llm_handle_prompts(json_data, batch_id, config)
    # Handle or save results as needed

if __name__ == "__main__":
    main()
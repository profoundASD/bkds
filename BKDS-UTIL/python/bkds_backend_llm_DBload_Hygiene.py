import argparse
import glob
import json
import os
import sys
import zipfile
from datetime import datetime
from bkds_Utilities import log_msg, db_load_llm_chat, load_and_resolve_config

"""
BKDS LLM Data Loader and Archiver

Purpose:
    This program automates the processing of JSON data files generated during LLM-based tasks. It performs
    two main functions: 
    1. Loads JSON data into a target database table.
    2. Archives processed files into a structured format for efficient management.

Logical Flow:
    1. **Argument Parsing**: Gathers runtime parameters including batch ID, configuration path, and config key.
    2. **Configuration Loading**: Dynamically loads and resolves configurations from a JSON file to define file paths,
       database schema, and other runtime behaviors.
    3. **Data Loading**: Matches and reads JSON files based on predefined patterns, then inserts the data into a target database.
    4. **Archiving**: Archives successfully processed files into a ZIP format to free up workspace and ensure data integrity.
    5. **Error Handling**: Logs and gracefully handles file, database, or configuration-related errors.

Usage:
    python bkds_llm_data_loader.py --batch_id <batch_id> --config_key <config_key> --config_path <config_file_path>

    - `--batch_id`: Unique identifier for the processing session.
    - `--config_key`: Key to access the specific configuration in the JSON file.
    - `--config_path`: Full path to the JSON configuration file.

Example:
    python bkds_llm_data_loader.py --batch_id example_batch123 --config_key BKDS_LLM_PROCESS_FLOW --config_path /path/to/config.json

Prerequisites:
    - Environment variable `BKDS_UTIL_DATA` must be set to specify the base directory for file processing.
    - Ensure the `bkds_Utilities` Python module is accessible in your runtime environment.
    - Database configurations and permissions should be correctly set to allow file insertion.

"""

# Name of the current program
program_name = os.path.basename(__file__)

######################################################################
# Argument Parsing
######################################################################

def parse_arguments():
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(description="Load LLM data into the database.")
    parser.add_argument('--batch_id', required=True, help='Unique batch ID for processing')
    parser.add_argument('--config_path', required=True, help='Path to the JSON configuration file')
    parser.add_argument('--config_key', required=True, help='Configuration key in the JSON file')
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
config_key = args.batch_id
config_file_path = args.config_path

######################################################################
# Configuration Constants and Defaults
######################################################################

# Environment variables and paths
BKDS_UTIL_ENV = "BKDS_UTIL_DATA"  # Environment variable for base directory
DEFAULT_OUTPUT_FOLDER = "output"

# Archive settings
ARCHIVE_FOLDER = "archive"
ARCHIVE_TYPE = "zip"  # Archive file type

# Configuration keys and defaults
ARCHIVE_SUBFOLDER = "archive_subfolder"
OUTPUT_SUBFOLDER_KEY = "output_subfolder"
PROCESS_SUBFOLDER_KEY = "process_subfolder"
TARGET_OBJECT_KEY = "target_object"
OUT_FILE_PREFIX_KEY = "out_file_prefix"
OUT_TYPE_KEY = "out_type"
TIMESTAMP_FORMAT_KEY = "timestamp_format"
TARGET_SCHEMA_KEY = "target_schema"

# Default values
DEFAULT_PREFIX = "bkds_llm"
DEFAULT_OUT_TYPE = "json"
DEFAULT_TARGET_SCHEMA = "dev"
DEFAULT_DATE_FORMAT = "%Y%m%d_%H%M%S"
TARGET_TABLE = "stg_llm_processed_contents"
PROCESS_SUBFOLDER = "process"

######################################################################
# Load Configuration
######################################################################

try:
    # Load and resolve configuration using the utility function
    config = load_and_resolve_config(config_key, config_path=config_file_path)
except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as e:
    log_msg(program_name, batch_id, f"Error loading configuration: {e}")
    sys.exit(1)

# Resolve configuration values or fallback to defaults
ARCHIVE_FOLDER = config.get(ARCHIVE_SUBFOLDER, ARCHIVE_FOLDER)
OUTPUT_SUBFOLDER = config.get(OUTPUT_SUBFOLDER_KEY, DEFAULT_OUTPUT_FOLDER)
PROCESS_SUBFOLDER = config.get(PROCESS_SUBFOLDER_KEY, PROCESS_SUBFOLDER)
TARGET_OBJECT = config.get(TARGET_OBJECT_KEY, TARGET_TABLE)
OUT_FILE_PREFIX = config.get(OUT_FILE_PREFIX_KEY, DEFAULT_PREFIX)
OUT_TYPE = config.get(OUT_TYPE_KEY, DEFAULT_OUT_TYPE)
TIMESTAMP_FORMAT = config.get(TIMESTAMP_FORMAT_KEY, DEFAULT_DATE_FORMAT)
TARGET_SCHEMA = config.get(TARGET_SCHEMA_KEY, DEFAULT_TARGET_SCHEMA)
file_pattern = f"{OUT_FILE_PREFIX}_{batch_id}_*.{OUT_TYPE}"

######################################################################
# Utility Functions
######################################################################

def logMsg(msg):
    """Log message to both standard output and log file."""
    log_msg(program_name, batch_id, msg)
    print(f"{msg}")

logMsg(f"{program_name} begins.")

def find_json_files_recursively(base_path, exclude_folder=ARCHIVE_FOLDER):
    """Find JSON files matching the file pattern, excluding a specified folder."""
    matched_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d != exclude_folder]  # Exclude specific folder
        for file in files:
            if glob.fnmatch.fnmatch(file, file_pattern):
                matched_files.append(os.path.join(root, file))
    return matched_files

######################################################################
# Main logic and functions
######################################################################

def run_data_loader(config_key):
    """Load data from JSON files into the database and archive processed files."""

    # Resolve output folder paths
    out_path = os.environ.get(BKDS_UTIL_ENV, '')
    if not out_path:
        logMsg(f"Environment variable '{BKDS_UTIL_ENV}' is not set.")
        sys.exit(1)
    logMsg(f'out_path: {out_path}')
    logMsg(f'BKDS_UTIL_ENV: {BKDS_UTIL_ENV}')

    out_folder = os.path.join(out_path, OUTPUT_SUBFOLDER, PROCESS_SUBFOLDER)
    archive_folder = os.path.join(out_folder, ARCHIVE_FOLDER)
    os.makedirs(archive_folder, exist_ok=True)

    # File matching pattern
    json_files = find_json_files_recursively(out_folder)

    if not json_files:
        logMsg(f"No JSON files found matching pattern: {file_pattern}")
        return False

    success = True
    processed_files = []
    failed_files = []

    for file_name in json_files:
        try:
            logMsg(f"Processing file: {file_name}")
            db_load_llm_chat(file_name, f"{TARGET_SCHEMA}.{TARGET_OBJECT}")
            logMsg(f"Successfully loaded data from: {file_name}")
            processed_files.append(file_name)
        except Exception as e:
            logMsg(f"Error processing file {file_name}: {e}")
            failed_files.append(file_name)
            success = False

    # Archive processed and failed files separately
    if processed_files:
        archive_files(processed_files, config_key)
    if failed_files:
        archive_failed_files(failed_files, config_key)

    logMsg(f"{program_name} ends with status: {'Success' if success else 'Failure'}.")
    return success


def archive_failed_files(failed_files, config_key):
    """Archive failed files into the archive folder with a FAILED_ prefix."""
    out_path = os.environ.get(BKDS_UTIL_ENV, '')
    if not out_path:
        logMsg(f"Environment variable '{BKDS_UTIL_ENV}' is not set.")
        sys.exit(1)

    archive_folder = os.path.join(out_path, OUTPUT_SUBFOLDER, PROCESS_SUBFOLDER, ARCHIVE_FOLDER)
    os.makedirs(archive_folder, exist_ok=True)  # Ensure the archive folder exists

    logMsg(f"Archiving failed files into: {archive_folder}")
    for file in failed_files:
        try:
            failed_file_name = f"FAILED_{os.path.basename(file)}"
            failed_file_path = os.path.join(archive_folder, failed_file_name)
            os.rename(file, failed_file_path)
            logMsg(f"Archived failed file: {failed_file_path}")
        except Exception as e:
            logMsg(f"Error archiving failed file {file}: {e}")


def archive_files(processed_files, config_key):
    """Archive processed files into a ZIP file."""
    out_path = os.environ.get(BKDS_UTIL_ENV, '')
    if not out_path:
        logMsg(f"Environment variable '{BKDS_UTIL_ENV}' is not set.")
        sys.exit(1)

    archive_folder = os.path.join(out_path, OUTPUT_SUBFOLDER, PROCESS_SUBFOLDER, ARCHIVE_FOLDER)
    os.makedirs(archive_folder, exist_ok=True)  # Ensure the archive folder exists

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    archive_file_name = f"{batch_id}_{config_key}_{timestamp}.{ARCHIVE_TYPE}"
    archive_file_path = os.path.join(archive_folder, archive_file_name)

    logMsg(f"Archiving processed files into: {archive_file_path}")
    try:
        with zipfile.ZipFile(archive_file_path, 'w') as zipf:
            for file in processed_files:
                arcname = os.path.basename(file)  # Use only the base name for the archive
                zipf.write(file, arcname)        # Add file to the archive
                os.remove(file)                 # Remove the original file after archiving

        logMsg(f"Archived and removed files: {processed_files}")
    except FileNotFoundError as e:
        logMsg(f"Error: Archive folder not found: {archive_folder}. Exception: {e}")
    except Exception as e:
        logMsg(f"Error archiving files: {e}")

######################################################################
# Main Function
######################################################################

def main():
    """Main function to run the data loader."""
    logMsg("Starting data loader.")
    success = run_data_loader(config_key)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

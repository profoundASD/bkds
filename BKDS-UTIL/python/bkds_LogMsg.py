"""
Utility Module for Logging in BKDS Applications

This module provides a centralized logging functionality for various BKDS applications. It configures and maintains loggers based on the combination of program names and batch IDs, ensuring that log messages are appropriately stored and formatted. Log files are created in a directory structure based on the hostname and date, facilitating easy organization and retrieval of logs.

Functions:
- log_msg(program_name, batch_id, message): Logs a message with a unique logger based on the program name and batch ID.
- logMsg(msg): A wrapper function to simplify logging within the module.

Usage:
This module is intended to be imported and used by other BKDS scripts. It requires environment variables for log paths and leverages Python's logging library for creating log files.

Note:
The script expects three command-line arguments - program_name, batch_id, and the message to log. An error message is displayed if the correct number of arguments is not provided.
"""
import os
import sys
import logging
from datetime import datetime, timezone
import socket
import argparse

#####################################################################
# Main Setup / Variables

# Set the log path
log_path = os.getenv("BKDS_LOGS")
if not log_path:
    raise ValueError("BKDS_LOGS environment variable is not set.")

# Using argparse to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Log messages for BKDS Applications.")
    parser.add_argument("program_name", help="Name of the program")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("message", help="Message to log")
    return parser.parse_args()

args = parse_arguments()
program_name = args.program_name
batch_id = args.batch_id
message = args.message

loggers = {}

########################################################################
#  Main logic and functions

def log_msg(program_name, batch_id, message):
    logger_key = f"{program_name}_{batch_id}"
    hostname = socket.gethostname()
    logger = logging.getLogger(f"{hostname}_{batch_id}_{program_name}")

    log_directory = os.path.join(log_path, hostname, datetime.now(timezone.utc).strftime('%Y%m%d'), batch_id)
    os.makedirs(log_directory, exist_ok=True)
    log_file_name = f"{hostname}_{batch_id}_{program_name}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}.log"
    log_file = os.path.join(log_directory, log_file_name)    

    if logger_key not in loggers:
        # Add file handler only if it doesn't already exist
        if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.baseFilename == log_file):
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False
            loggers[logger_key] = logger

    try:
        logger.info(message)
        for handler in logger.handlers:
            handler.flush()
    except Exception as e:
        print(f"Error while logging: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python script_name.py program_name batch_id message {sys.argv}")
        sys.exit(1)

    # Log the message
    log_msg(program_name, batch_id, message)

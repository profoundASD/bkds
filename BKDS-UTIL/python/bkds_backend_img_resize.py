#!/usr/bin/env python3

"""
Image Size Analyzer and Resizer

This script scans a directory to analyze and conditionally resize image files 
(.png, .jpg, .jpeg). Images over specified dimensions or file size can be resized 
to meet defined requirements. Optionally, it outputs a report with detailed file size 
categories.

Usage:
    ./image_size_analyzer.py <batch_id> <min_size_mb> <min_intrinsic> <resize_flag>
"""

import os
import argparse
from collections import defaultdict
from PIL import Image, ImageFile
import warnings
from bkds_Utilities import log_msg
from concurrent.futures import ThreadPoolExecutor, as_completed

#####################################################################
# Argument Parsing

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze and resize image files in a directory")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("min_size_mb", type=int, help="Minimum file size in MB for resizing")
    parser.add_argument("min_intrinsic", type=int, help="Minimum intrinsic width for resizing")
    parser.add_argument("resize_flag", choices=["Y", "N"], help="Whether to resize for file size reduction (Y/N)")
    return parser.parse_args()

args = parse_arguments()
BATCH_ID = args.batch_id
MIN_SIZE_BYTES = args.min_size_mb * 1024 * 1024  # Convert MB to bytes
MIN_INTRINSIC_WIDTH = args.min_intrinsic
RESIZE_FOR_SIZE = args.resize_flag == "Y"

#####################################################################
# Configuration and Constants

SIZE_CATEGORIES = [
    (10 * 1024, "< 10KB"),
    (20 * 1024, "10KB - 20KB"),
    (50 * 1024, "20KB - 50KB"),
    (100 * 1024, "50KB - 100KB"),
    (200 * 1024, "100KB - 200KB"),
    (500 * 1024, "200KB - 500KB"),
    (1 * 1024 * 1024, "500KB - 1MB"),
    (2 * 1024 * 1024, "1MB - 2MB"),
    (3 * 1024 * 1024, "2MB - 3MB"),
    (4 * 1024 * 1024, "3MB - 4MB"),
    (5 * 1024 * 1024, "4MB - 5MB"),
    (10 * 1024 * 1024, "5MB - 10MB"),
    (float('inf'), "> 10MB")
]

# Initialize counters (to be used in the main thread)
file_counts = defaultdict(lambda: defaultdict(int))
resize_counts = {"resized": 0, "skipped": 0, "failed": 0}

NODEJS_DATA = os.getenv('BKDS_NODEJS_DATA', '/default/path/for/nodejs_data')
IMG_DATA = os.path.join(NODEJS_DATA, 'images')
PROGRAM_NAME = os.path.basename(__file__)

def logMsg(msg):
    """Log a message to the console and using a logging system."""
    log_msg(PROGRAM_NAME, BATCH_ID, msg)
    print(msg)

#####################################################################
# Helper Functions

def categorize_file_size(file_size):
    """Return the size category label for a given file size."""
    for size_limit, label in SIZE_CATEGORIES:
        if file_size <= size_limit:
            return label
    return "> 10MB"

def scan_directory(directory):
    """Recursively scan directory and collect image file paths and sizes."""
    image_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            ext = filename.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png']:
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                image_files.append((file_path, file_size))
    return image_files

def process_chunk(chunk_files, reporting_only=False):
    """Process a chunk of image files or gather report data."""
    thread_file_counts = defaultdict(lambda: defaultdict(int))
    if reporting_only:
        for file_path, file_size in chunk_files:
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            size_category = categorize_file_size(file_size)
            thread_file_counts[ext][size_category] += 1
    else:
        # Actual resizing logic goes here for non-reporting mode
        pass

    return thread_file_counts

def split_list(lst, n):
    """Split lst into n approximately equal chunks."""
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

#####################################################################
# Report Generation

def merge_counts(global_counts, thread_counts):
    """Merge per-thread counts into the global counts."""
    for key, value in thread_counts.items():
        if isinstance(value, dict):
            if key not in global_counts:
                global_counts[key] = defaultdict(int)
            for subkey, subvalue in value.items():
                global_counts[key][subkey] += subvalue
        else:
            global_counts[key] += value

def print_report():
    """Print a summary report of the file counts by type and size category."""
    print("\n\nImage File Size Report:")
    for file_type, sizes in file_counts.items():
        print(f"\n{file_type.upper()} Files:")
        for size_category, count in sizes.items():
            print(f"  {size_category}: {count} files")

#####################################################################
# Main Execution

if __name__ == "__main__":
    directory_to_scan = IMG_DATA

    if not os.path.isdir(directory_to_scan):
        print(f"Error: '{directory_to_scan}' is not a valid directory.")
        exit(1)

    print(f"Scanning directory: {directory_to_scan}")
    all_image_files = scan_directory(directory_to_scan)
    
    # If reporting mode, skip other arguments and generate only the report
    reporting_only = BATCH_ID == "BKDS_IMG_RESIZE_REPORT"
    if reporting_only:
        chunks = split_list(all_image_files, 10)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_chunk, chunk, reporting_only=True) for chunk in chunks]
            for future in as_completed(futures):
                thread_file_counts = future.result()
                merge_counts(file_counts, thread_file_counts)
        print_report()
    else:
        # Non-reporting mode: filter and process images based on size and intrinsic width
        filtered_files = [
            (file_path, size) for file_path, size in all_image_files 
            if size > MIN_SIZE_BYTES or Image.open(file_path).size[0] > MIN_INTRINSIC_WIDTH
        ]
        
        # Split filtered files into chunks
        chunks = split_list(filtered_files, 10)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_chunk, chunk, reporting_only=False) for chunk in chunks]
            for future in as_completed(futures):
                thread_file_counts = future.result()
                merge_counts(file_counts, thread_file_counts)

        print_report()

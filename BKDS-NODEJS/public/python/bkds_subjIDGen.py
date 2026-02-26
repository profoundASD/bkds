import argparse
import json
import hashlib
from datetime import datetime
import random
import os

def generate_subjID(category, _type, subject, keyword):
    # Create a unique hash using category, type, subject, keyword, timestamp, and randomness
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Up to millisecond precision
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))  # You can adjust the length as needed
    data_to_hash = f"{category}{_type}{subject}{keyword}{timestamp}{random_string}"
    subjID = hashlib.sha256(data_to_hash.encode()).hexdigest()
    return subjID

def main():
    parser = argparse.ArgumentParser(description="Generate subjIDs for JSON data.")
   # parser.add_argument("subj", help="String for subj")
 #   args = parser.parse_args()
    
 #   subj = args.subj
    input_directory = '../data/subjects/old'
    output_directory = '../data/subjects/'

    for filename in os.listdir(input_directory):
        if filename.endswith(f'_subj.json'):
            print(f'found subj {filename}')
            input_file = os.path.join(input_directory, filename)
            output_file = os.path.join(output_directory, f'{filename}')
            
            with open(input_file, 'r') as f:
                data = json.load(f)

            for entry in data:
                print(f'processing entry {entry}')
                entry['subjID'] = generate_subjID(
                    entry['category'], entry['type'], entry['subject'], entry['keyword']
                )

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=4)

if __name__ == '__main__':
    main()

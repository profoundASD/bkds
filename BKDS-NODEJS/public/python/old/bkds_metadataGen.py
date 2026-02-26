import os
import json
import argparse

def main():
    input_directory = '../data/subjects/'
    output_file = '../data/output/unique_categories_and_subjects.json'
    
    unique_combinations = set()  # To store unique category and subject combinations

    for filename in os.listdir(input_directory):
        print(f'filename: {filename}')
        if filename.endswith('_subj.json'):
            input_file = os.path.join(input_directory, filename)

            with open(input_file, 'r') as f:
                data = json.load(f)

            for entry in data:
                print(f'entry: {entry}')
                category = entry['category']
                subject = entry['subject']
                unique_combinations.add((category, subject))

    unique_combinations_list = [{'category': category, 'subject': subject} for category, subject in unique_combinations]

    with open(output_file, 'w') as f:
        json.dump(unique_combinations_list, f, indent=4)

if __name__ == '__main__':
    main()

import json

def process_json_file(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    output_data = []
    for entry in data:
        group_name = entry.get('GROUP_NAME', 'N/A')
        access_name_alt = entry.get('ACCESS_NAME_ALT', 'N/A')

        output_data.append({"SUBJECT": group_name, "KEYWORD": access_name_alt})

    with open(output_file, 'w') as file:
        json.dump(output_data, file, indent=4)

# Example usage
input_file_path = '../data/output/metadata_20231224190502.json'  # Replace with your JSON file path
output_file_path = '../data/output/bkds_aviation_subj.json'  # The output file path

process_json_file(input_file_path, output_file_path)

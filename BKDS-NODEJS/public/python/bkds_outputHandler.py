import json
import os
import re

def subjGen_save_to_json(out_dir, data, subjType, output_prefix, output_type, keyword, subjID, timestamp):
    """
    Saves the processed data to a JSON file.
    
    :param out_dir: Output directory.
    :param data: Data to be saved.
    :param subjType: Subject type.
    :param output_prefix: Prefix for the output filename.
    :param output_type: Type of the output file.
    :param keyword: The keyword used for searching.
    :param subjID: Subject ID.
    :param timestamp: Timestamp for the filename.
    :return: The path of the saved file.
    """
    category_cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', data[-1]['category']).replace(' ', '_')
    keyword_cleaned = re.sub(r'[^a-zA-Z0-9_]+', '_', keyword).strip('_')
    output_filepath = os.path.join(out_dir, f'{subjType}/{output_prefix}_{subjType}_{keyword_cleaned}_{subjID}_{timestamp}.{output_type}')
    output_filepath = output_filepath.replace('__', '_')
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    with open(output_filepath, 'w') as output_file:
        json.dump(data, output_file, indent=4)

    return output_filepath

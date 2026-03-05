import json
import hashlib

def generate_insight_id(search_term, page_url, category):
    """
    Generate a unique hash based on the concatenation of the first 100 bytes of 
    the search term, page URL, and category.
    """
    combined_string = f"{search_term}{page_url}{category}".encode('utf-8')[:100]
    return hashlib.sha256(combined_string).hexdigest()

def add_insight_id_to_json(file_path):
    try:
        # Load the JSON data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Add insightID to each entry
        for entry in data:
            search_term = entry.get("Search Term", "")
            page_url = entry.get("Page URL", "")
            category = entry.get("category", "")
            entry["insightID"] = generate_insight_id(search_term, page_url, category)

        # Write the updated data back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        return "JSON file updated successfully."

    except Exception as e:
        return f"An error occurred: {str(e)}"

# To use the script, replace 'path_to_your_json_file.json' with the actual file path
# file_path = 'path_to_your_json_file.json'
# result = add_insight_id_to_json(file_path)
# print(result)

def main():
    print('running...')
    add_insight_id_to_json('../data/output/bkds_lake_subj_20231231_164912.json')

# Running the main function and getting the path of the output file
main()

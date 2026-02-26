import json
import string

def normalize_string_for_comparison(s):
    """
    Normalize a string for comparison by removing punctuation
    and converting to lowercase, without trimming spaces.
    """
    # Remove punctuation and convert to lowercase
    return ''.join(char for char in s if char not in string.punctuation).lower()

def deduplicate_banned_words(file_path):
    """
    Deduplicate and normalize the bannedWordList in a JSON file.
    """
    # Load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Check if the JSON structure contains the 'bannedWordList' key
    if not isinstance(data.get("bannedWordList"), list):
        raise ValueError('"bannedWordList" must be a list in the JSON file.')

    # Deduplicate while preserving original strings
    normalized_set = set()
    deduplicated_banned_words = []

    for word in data["bannedWordList"]:
        normalized = normalize_string_for_comparison(word)
        if normalized not in normalized_set:
            normalized_set.add(normalized)
            # Preserve the original string without removing spaces
            deduplicated_banned_words.append(word.lower())

    # Update the JSON object
    data["bannedWordList"] = deduplicated_banned_words

    # Write the updated JSON back to a new file
    output_file_path = file_path.replace('.json', '_deduplicated.json')
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f'Deduplicated bannedWordList written to: {output_file_path}')

# Example usage
if __name__ == "__main__":
    input_file = '/home/aimless76/Documents/Sync/BKDS/BKDS-APP/BKDS-NODEJS/public/data/config/bkds_bannedWords.json'  # Replace with your actual file path
    deduplicate_banned_words(input_file)

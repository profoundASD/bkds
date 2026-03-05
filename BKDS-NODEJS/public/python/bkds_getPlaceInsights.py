import json

def extract_insights(json_data):
    # Extracting the relevant data from the JSON input
    insights = []
    for item in json_data:
        subject = item.get("type", "")
        keywords = item.get("insightSubject", "")
        insights.append({"Subject": subject, "Keywords": keywords})
    
    return insights

def read_json_file(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json_file(file_path, data):
    """Writes data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def process_insights(input_path, output_path):
    # Read the JSON data from the file
    json_data = read_json_file(input_path)

    # Extract insights
    insights = extract_insights(json_data)

    # Write the extracted insights to a new JSON file
    write_json_file(output_path, insights)

def main():
    input_path = '../data/config/bkds_PlaceInsights.json'
    output_path = '../data/output/bkds_PlaceInsights_out.json'

    process_insights(input_path, output_path)
    print(f"Insights extracted and saved to {output_path}")

# Running the main function
if __name__ == "__main__":
    main()


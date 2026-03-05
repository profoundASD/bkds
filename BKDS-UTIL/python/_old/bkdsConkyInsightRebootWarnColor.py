import sys
import json

# Function to get reboot status from a JSON file
def get_reboot_status(json_path):
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        return data.get('reboot_required', '')
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bkdsWarn.py <path_to_json_file>")
        sys.exit(1)

    json_path = sys.argv[1]
    reboot_status = get_reboot_status(json_path)
    print(reboot_status)

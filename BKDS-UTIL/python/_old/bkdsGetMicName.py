import subprocess
import re

def get_microphone_name():
    try:
        # Run the command and capture its output
        output = subprocess.check_output("pactl list sources | awk -v RS='' '/Description:.*Microphone/ && /Active Port: analog-input-mic/{gsub(/^.*Description: /, \"\"); print}'", shell=True, text=True)

        # Define a regular expression pattern to match 'device.product.name'
        pattern = r'device\.product\.name = "([^"]+)"'

        # Use re.search to find the first match
        match = re.search(pattern, output)

        # Extract and return the 'device.product.name' if found
        if match:
            product_name = match.group(1)
            return product_name
        else:
            return "Device product name not found"

    except subprocess.CalledProcessError:
        return "Error executing the command"

# Call the function to get the microphone name
microphone_name = get_microphone_name()

# Print or use the extracted name as needed
print(microphone_name)

import subprocess
import re
import json

def parse_top_output(output):
    data = {}
    
    # Extract CPU and memory usage using regular expressions
    cpu_usage = re.search(r"%Cpu\(s\): (\d+\.\d+)% us,", output)
    memory_usage = re.search(r"KiB Mem : (\d+) total,\s+(\d+) free,", output)
    
    if cpu_usage:
        data["CPU Usage (%)"] = float(cpu_usage.group(1))
    
    if memory_usage:
        data["Memory Total (KB)"] = int(memory_usage.group(1))
        data["Memory Free (KB)"] = int(memory_usage.group(2))

    return data

def main():
    try:
        # Run 'top' and capture its output
        top_output = subprocess.check_output(["top", "-n", "1", "-b"]).decode("utf-8")
        
        # Parse the output
        parsed_data = parse_top_output(top_output)

        # Dump the data to a JSON file
        with open("top_report.json", "w") as json_file:
            json.dump(parsed_data, json_file, indent=4)
        
        print("JSON report saved to 'top_report.json'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

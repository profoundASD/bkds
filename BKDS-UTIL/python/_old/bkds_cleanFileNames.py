import os
import re
import unicodedata

def clean_name(name):
    """Clean up names by applying various transformations."""
    # Replace specific strings in aircraft models
    aircraft_models = {
        "B 52": "B-52",
        "B  52": "B-52",
        "B52": "B-52",
        "B52": "B-52",
        "C 130": "C-130",
        "C  130": "C-130",
        "B 25": "B-25",
        "B25": "B-25",
        "B-25-Mitchell": "B-25 Mitchell",
        "KC 10": "KC-10",
        "KC  10": "KC-10",
        "B 1B" : "B-1B",
        "B 17" : "B-17",
        "B  17" : "B-17",
        "B17" : "B-17",
        "F 15" : "F-15",
        "F  15" : "F-15",
        "F15" : "F-15",
        "F 16" : "F-16",
        "F  16" : "F-16",
        "F16" : "F-16"    }
    for model, replacement in aircraft_models.items():
        name = name.replace(model, replacement)

    # Normalize string and replace specific characters
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r"[ \-:;,'\"\(\)\[\]±%*&#@~=\n]+", "_", name)
    name = re.sub(r'\d{5,}', '', name)

    # Remove size strings
    size_strings = [
        "640px", "800px", "1024px", "1280px",
        "1920px", "300px", "600px", "1200px",
        "1600px", "2048px"
    ]

    for size_string in size_strings:
        name = name.replace(size_string, '')

    # Collapse multiple underscores and remove leading/trailing underscores
    name = re.sub(r"_+", "_", name).strip('_')

    # Replace specific extensions
    extension_mappings = {".svg.png": ".png"}
    for ext, replacement in extension_mappings.items():
        if name.endswith(ext):
            name = name[:-len(ext)] + replacement

    return name

def rename_files_in_directory(directory):
    """Walk through the directory and rename files and directories."""
    # Rename files
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            new_name = clean_name(file)
            if new_name != file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed file '{old_path}' to '{new_path}'")

def replace_extensions(filename, extension_mappings):
    """Replace file extensions based on the provided mapping."""
    for ext, replacement in extension_mappings.items():
        if filename.endswith(ext):
            return filename[:-len(ext)] + replacement
    return filename

def replace_aircraft_models(filename, model_mappings):
    """Replace aircraft model strings based on provided mappings."""
    for model, replacement in model_mappings.items():
        filename = filename.replace(model, replacement)
    return filename

def normalize_string(input_string):
    """Normalize the given string to its closest ASCII representation."""
    return unicodedata.normalize('NFD', input_string).encode('ascii', 'ignore').decode('ascii')

def rename_files_in_directory(directory):
    """Walk through the directory and rename files and directories."""
    # Rename files
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            new_name = clean_name(file)
            if new_name != file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed file '{old_path}' to '{new_path}'")

    # Rename directories
    for root, dirs, _ in os.walk(directory, topdown=False):
        for dir in dirs:
            new_name = clean_name(dir)
            if new_name != dir:
                old_path = os.path.join(root, dir)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed directory '{old_path}' to '{new_path}'")

def main():
    base_dir = "/home/aimless76/Documents/Sync/BKDS/BKDS_APP/tmp-data"
    rename_files_in_directory(base_dir)

if __name__ == "__main__":
    main()

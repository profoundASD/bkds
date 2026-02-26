import time
import os
import json
from PIL import Image
import imghdr

# Constants and configurations
sizes = [200]
suffixes = ["_PIL_200.jpg"]
valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
MAX_FILENAME_LENGTH = 200  # Typical max filename length in Linux
MAX_PATH_LENGTH = 255  # Typical max path length in Linux

def sanitize_filename(filename):
    """Sanitize the filename by removing unsafe characters and replacing spaces with underscores."""
    return filename.replace(' ', '_').replace("'", "''")

def parse_friendly_name(filename):
    """Extract the friendly name from the filename."""
    parts = filename.split('_')
    if len(parts) > 4:
        return '_'.join(parts[4:]).split('_PIL_')[0].replace('_', ' ')
    return ' '.join(parts[4:])

def truncate_filename(filename, max_length):
    """Truncate the filename to ensure it does not exceed the maximum allowed length."""
    if len(filename) <= max_length:
        return filename
    base_name, ext = os.path.splitext(filename)
    allowed_length = max_length - len(ext)
    truncated_base_name = base_name[:allowed_length]
    return truncated_base_name + ext

def truncate_path(filepath, max_path_length):
    """Truncate the filepath to ensure it does not exceed the maximum allowed length."""
    if len(filepath) <= max_path_length:
        return filepath
    dirname, filename = os.path.split(filepath)
    # Calculate the maximum allowed filename length based on the directory length
    max_filename_length = max_path_length - len(dirname) - 1
    truncated_filename = truncate_filename(filename, max_filename_length)
    return os.path.join(dirname, truncated_filename)

def detect_and_correct_image_type(filepath):
    """Detect the actual image type and correct the file extension if necessary."""
    if not os.path.exists(filepath):
        return None
    
    detected_type = imghdr.what(filepath)
    if detected_type:
        detected_ext = f".{detected_type}"
        actual_path = filepath
        if not filepath.lower().endswith(detected_ext):
            actual_path = filepath[:filepath.rfind('.')] + detected_ext
            actual_path = truncate_path(actual_path, MAX_PATH_LENGTH)
            os.rename(filepath, actual_path)
        return actual_path
    return None

def generate_thumbnails(source_directory, target_directory, source_type):
    # Counters for reporting
    generated_count = 0
    skipped_count = 0
    manifest_data = []

    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)

    # Gather all files in the source directory that do not have _PIL_ in the name
    base_files = [f for f in os.listdir(source_directory) if os.path.isfile(os.path.join(source_directory, f)) and "_PIL_" not in f]

    print(f"Found {len(base_files)} base files to process.")

    for base_file in base_files:
        base_name, ext = os.path.splitext(base_file)

        # Skip non-image files
        if ext.lower() not in valid_extensions:
            print(f"Skipping non-image file: {base_file}")
            continue

        for size, suffix in zip(sizes, suffixes):
            pil_version = base_name + suffix
            pil_path = os.path.join(target_directory, pil_version)
            pil_path = truncate_path(pil_path, MAX_PATH_LENGTH)

            # If the _PIL_ version does not exist in the target directory, create it
            if not os.path.exists(pil_path):
                img_path = os.path.join(source_directory, base_file)
                corrected_img_path = detect_and_correct_image_type(img_path)

                if not corrected_img_path:
                    print(f"Skipping file with unknown type: {img_path}")
                    continue

                try:
                    print('trying to open image:', corrected_img_path)
                    with Image.open(corrected_img_path) as img:
                        print('opened image:', corrected_img_path)
                        img.verify()  # Verify the image can be opened
                        print('verified image:', corrected_img_path)
                        
                        img = Image.open(corrected_img_path)  # Reopen image after verify
                        print('reopened image for copy:', corrected_img_path)
                        
                        # Handle different image modes properly
                        if img.mode not in ("RGB", "RGBA", "P"):
                            print('converting image to RGB')
                            img = img.convert("RGB")

                        img_copy = img.copy()
                        print('copied image:', corrected_img_path)
                        
                        img_copy.thumbnail((size, size), Image.LANCZOS)
                        print('created thumbnail:', corrected_img_path)
                        
                        # Convert to RGB mode if the image has an alpha channel
                        if img_copy.mode in ("RGBA", "P"):
                            img_copy = img_copy.convert("RGB")

                        # Generate the PIL version file name
                        pil_filename = os.path.basename(corrected_img_path).replace(ext, suffix)
                        pil_filename = truncate_filename(pil_filename, MAX_FILENAME_LENGTH)
                        pil_path = os.path.join(target_directory, pil_filename)
                        pil_path = truncate_path(pil_path, MAX_PATH_LENGTH)

                        img_copy.save(pil_path, "JPEG")
                        print(f"Created {pil_path}")
                        generated_count += 1

                        # Add to manifest
                        friendly_name = parse_friendly_name(base_file)
                        manifest_data.append({
                            'raw_file_name': base_file,
                            'raw_file_path': corrected_img_path,
                            'thumbnail_file_path': pil_path,
                            'friendly_name': friendly_name,
                            'source': source_type  # 'flickr', 'wiki', 'youtube', etc.
                        })
                except Exception as e:
                    print(f"Failed to create {pil_path}: {e}")
            else:
                print(f"Skipped existing file: {pil_path}")
                skipped_count += 1

    print(f"Total files generated: {generated_count}")
    print(f"Total files skipped: {skipped_count}")

    return manifest_data

def main(source_type):
    env_dir = os.getenv('BKDS_NODEJS_DATA')
    if source_type not in ["flickr", "wiki", "youtube"]:
        print("Invalid source type. Please choose from 'flickr', 'wiki', or 'youtube'.")
        return
    
    source_directory = os.path.join(env_dir, "images/full_size", source_type)
    target_directory = os.path.join(env_dir, "images/full_size", source_type)
    manifest_file = os.path.join(env_dir, f'{source_type}_img_manifest.json')

    print(f"Environment Directory: {env_dir}")
    print(f"Source Directory: {source_directory}")
    print(f"Target Directory: {target_directory}")

    print(f"Starting thumbnail generation in directory: {source_directory}")
    manifest_data = generate_thumbnails(source_directory, target_directory, source_type)
    print("Thumbnail generation completed.")

    # Write manifest to JSON file
    with open(manifest_file, 'w') as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Manifest file written to {manifest_file}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <source_type>")
        sys.exit(1)
    source_type = sys.argv[1]
    main(source_type)

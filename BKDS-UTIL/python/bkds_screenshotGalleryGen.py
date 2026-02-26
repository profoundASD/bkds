import os
import json
from datetime import datetime
import shutil
import subprocess
os.environ["DISPLAY"] = os.getenv("DISPLAY", ":0")
##############################################################################
# Global Variables for Image Indexing
SOURCE_DIR = os.getenv("BKDS_REPORTING_DATA", "/default/source/directory")
INDEX_FILE = os.path.join(os.getenv("BKDS_UTIL_DATA", "/default/util/data"), "config", "index.json")

SOURCE_DIR='/home/aimless76/Documents/Sync/BKDS/BKDS-APP/BKDS-BACKEND/BKDS-AUTOMATION-CONFIG/reporting/data/'
IMG_DIR = SOURCE_DIR

# Supported image file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

##############################################################################

# Helper Functions

def get_file_metadata(file_path):
    """Retrieve metadata for a given file."""
    stats = os.stat(file_path)
    return {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": os.path.splitext(file_path)[1].lower(),
        "created_date": datetime.fromtimestamp(stats.st_ctime).isoformat(),
        "modified_date": datetime.fromtimestamp(stats.st_mtime).isoformat(),
    }

def load_index():
    """Load the image index from the JSON file."""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as file:
            return json.load(file)
    return []

def save_index(data):
    """Save the updated image index to the JSON file."""
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w") as file:
        json.dump(data, file, indent=4)

def find_new_images(source_dir, indexed_paths):
    """Find new images in the source directory not present in the index."""
    new_images = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS and file_path not in indexed_paths:
                new_images.append(file_path)
    return new_images

def copy_images_to_img_dir(images, img_dir):
    """Copy new images to the img directory."""
    os.makedirs(img_dir, exist_ok=True)
    copied_paths = []
    for image in images:
        destination = os.path.join(img_dir, os.path.basename(image))
        if not os.path.samefile(image, destination):
            shutil.copy2(image, destination)
        copied_paths.append(destination)
    return copied_paths

def open_gallery_with_gthumb(img_dir):
    """Open all images in the img directory sorted by modified date descending."""
    images = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))]
    sorted_images = sorted(images, key=lambda x: os.path.getmtime(x), reverse=True)

    # Get the environment and ensure DISPLAY is set
    env = os.environ.copy()
    env["DISPLAY"] = env.get("DISPLAY", ":0")
    
    # Launch gthumb
    subprocess.run(["gthumb"] + sorted_images, env=env)

##############################################################################
# Main Function

def main():
    print("Starting image indexing process...")

    # Load the current index
    index = load_index()
    indexed_paths = {item["file_path"] for item in index}

    # Find new images
    new_images = find_new_images(SOURCE_DIR, indexed_paths)

    if new_images:
        print(f"Found {len(new_images)} new images. Indexing...")
        for image in new_images:
            metadata = get_file_metadata(image)
            index.append(metadata)

        # Copy new images to img directory
        copied_images = copy_images_to_img_dir(new_images, IMG_DIR)

        # Save the updated index
        save_index(index)
        print(f"Indexed {len(new_images)} new images and copied to img directory.")
    else:
        print("No new images to index.")

    # Open gallery with gthumb
    print("Opening gallery with gthumb...")
    open_gallery_with_gthumb(IMG_DIR)

if __name__ == "__main__":
    main()
import os
import shutil
import hashlib
from collections import defaultdict

# Environment variable
node_dir = os.getenv('BKDS_NODEJS_DATA')
node_dir = os.path.join(node_dir, 'image')

print(f'Working on {node_dir}')

# Directories for moving files
flex_size_dirs = {
    'wiki': os.path.join(node_dir, 'new_img', 'flex_size', 'wiki'),
    'youtube': os.path.join(node_dir, 'new_img', 'flex_size', 'youtube'),
    'flickr': os.path.join(node_dir, 'new_img', 'flex_size', 'flickr')
}

full_size_dirs = {
    'wiki': os.path.join(node_dir, 'new_img', 'full_size', 'wiki'),
    'youtube': os.path.join(node_dir, 'new_img', 'full_size', 'youtube'),
    'flickr': os.path.join(node_dir, 'new_img', 'full_size', 'flickr')
}

# Create directories if they do not exist
for dir_path in flex_size_dirs.values():
    os.makedirs(dir_path, exist_ok=True)

for dir_path in full_size_dirs.values():
    os.makedirs(dir_path, exist_ok=True)

# Function to move files based on their names
def move_files(src_dir, dest_dirs):
    print(f'Move files from {src_dir} to {dest_dirs}')
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            src_file = os.path.join(root, file)
            print(f'Moving file: {src_file}')
            if 'wiki' in file:
                dest_file = os.path.join(dest_dirs['wiki'], file)
            elif 'youtube' in file:
                dest_file = os.path.join(dest_dirs['youtube'], file)
            elif 'flickr' in file:
                dest_file = os.path.join(dest_dirs['flickr'], file)
            else:
                continue
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.move(src_file, dest_file)

def main():
    # Organize files under 'pil'
    for root, dirs, files in os.walk(node_dir):
        for dir_name in dirs:
            if dir_name == 'pil':
                pil_path = os.path.join(root, dir_name)
                move_files(pil_path, flex_size_dirs)

    # Organize files not under 'pil'
    for root, dirs, files in os.walk(node_dir):
        for dir_name in dirs:
            if dir_name != 'pil' and not dir_name.startswith('new_img'):
                non_pil_path = os.path.join(root, dir_name)
                move_files(non_pil_path, full_size_dirs)

    print("Script execution completed.")

if __name__ == "__main__":
    main()

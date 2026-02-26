import time
import os

def remove_files_with_multiple_pil(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            print(f'checking {file}')
            if file.count('PIL') > 1:
                print(f'multi PIL {file}')
                time.sleep(2)
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
                    time.sleep(2)
                except Exception as e:
                    print(f"Failed to remove file: {file_path}, error: {e}")

# Example usage:
directory_path = '/home/aimless76/Documents/dev/util/image_cache/yt/pil'
remove_files_with_multiple_pil(directory_path)

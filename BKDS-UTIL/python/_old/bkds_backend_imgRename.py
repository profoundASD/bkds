import os

def rename_files(directory):
    # Get a list of all files in the directory
    files = os.listdir(directory)
    
    for file in files:
        # Check if the file ends with .jpeg
        if file.endswith('.jpeg'):
            # Define the new filename
            new_file = file.replace('.jpeg', '.jpg')
            
            # Get the full paths
            old_file_path = os.path.join(directory, file)
            new_file_path = os.path.join(directory, new_file)
            
            # Check if the new filename already exists
            if os.path.exists(new_file_path):
                print(f"Skipping {file} because {new_file} already exists.")
            else:
                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f"Renamed {file} to {new_file}")

if __name__ == '__main__':
    directory = input("Enter the directory path where you want to rename files: ")
    if os.path.isdir(directory):
        rename_files(directory)
    else:
        print("The provided path is not a valid directory.")

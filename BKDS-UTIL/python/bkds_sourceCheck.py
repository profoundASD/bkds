import os
import filecmp
from pathlib import Path

# List of file extensions to consider
FILE_EXTENSIONS = {".sh", ".py", ".js", ".css", ".ejs", ".html"}

# List of directories to exclude
EXCLUDE_DIRS = {"/home/aimless76/Documents/Sync/BKDS/BKDS-APP-DEV/BKDS-NODEJS/node_modules", "/path/to/exclude2"}

# List of file patterns to exclude
EXCLUDE_PATTERNS = ["*.sync-conflict*"]

def find_newer_and_different_files(dir1, dir2):
    """
    Compare files in dir1 against dir2 and find files that are newer and different in dir1.

    :param dir1: Path to the first directory.
    :param dir2: Path to the second directory.
    :return: List of tuples (file_path_in_dir1, file_path_in_dir2)
    """
    updated_files = []

    for root, _, files in os.walk(dir1):
        # Skip excluded directories
        if any(Path(root).resolve().as_posix().startswith(Path(exclude).resolve().as_posix()) for exclude in EXCLUDE_DIRS):
            continue

        for file in files:
            # Skip excluded patterns
            if any(Path(file).match(pattern) for pattern in EXCLUDE_PATTERNS):
                continue

            ext = Path(file).suffix
            if ext in FILE_EXTENSIONS:
                file_path_dir1 = Path(root) / file
                file_path_dir2 = Path(dir2) / os.path.relpath(file_path_dir1, dir1)

                if file_path_dir2.exists():
                    # Compare modification times and content
                    if (file_path_dir1.stat().st_mtime > file_path_dir2.stat().st_mtime and
                        not filecmp.cmp(file_path_dir1, file_path_dir2, shallow=False)):
                        updated_files.append((file_path_dir1, file_path_dir2))
                else:
                    # File doesn't exist in dir2, consider it newer
                    updated_files.append((file_path_dir1, file_path_dir2))

    return updated_files

def generate_copy_commands(updated_files):
    """
    Generate shell commands to copy newer and different files over.

    :param updated_files: List of tuples (source_file, destination_file).
    :return: List of shell commands as strings.
    """
    commands = []

    for src, dest in updated_files:
        dest_dir = os.path.dirname(dest)
        commands.append(f"mkdir -p \"{dest_dir}\"")  # Ensure the destination directory exists
        commands.append(f"cp \"{src}\" \"{dest}\"")  # Copy the file

    return commands

def main():
    dir1 = '/home/aimless76/Documents/Sync/BKDS/BKDS-APP-DEV'
    dir2 = '/home/aimless76/Documents/Sync/BKDS/BKDS-APP'


    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        print("Both paths must be valid directories.")
        return

    updated_files = find_newer_and_different_files(dir1, dir2)

    if not updated_files:
        print("No newer or different files found.")
        return

    commands = generate_copy_commands(updated_files)

    # Output commands to a script file
    script_file = "copy_newer_files.sh"
    with open(script_file, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("\n".join(commands))

    # Make the script executable
    os.chmod(script_file, 0o755)

    print(f"Generated script: {script_file}")
    print("Run the script to copy the newer files.")

if __name__ == "__main__":
    main()
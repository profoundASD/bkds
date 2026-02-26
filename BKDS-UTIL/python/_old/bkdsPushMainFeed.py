import os
import shutil
import datetime

# Step 1: Get latest file from Directory1 with pattern "*main*feed*.html" (case-insensitive)
directory1 = "/home/aimless/BKDS-APP/ContentGen/wip/html_data"
pattern = "hjMainFeed"

files = [f for f in os.listdir(directory1) if f.lower().startswith(pattern.lower()) and f.lower().endswith('.html')]
# print(os.listdir(directory1))
print('pattern: ', directory1, pattern)
if not files:
    print("No file found in Directory1 matching pattern:", pattern)
    exit()

new_file =max(files)
new_file_path = os.path.join(directory1, new_file)

print('files', new_file_path)

# Step 2: Get OldFile called index.html from directory
directory = "/home/aimless/BKDS-APACHE-WEB-01/bkds/web/html/main/"
old_file_path = os.path.join(directory, "index.html")
print('old_file_path', old_file_path)
# Step 3: Compare NewFile to OldFile
if not os.path.exists(old_file_path):
    print("OldFile does not exist")
    exit()
with open(new_file_path, "r") as f1, open(old_file_path, "r") as f2:
    new_content = f1.read()
    old_content = f2.read()
if new_content == old_content:
    print("NewFile and OldFile have the same content")
    exit()

# Step 4: Rename OldFile to index.html_[timestamp], Rename NewFile to index.html,
# and retain a copy of OldFile now named index.html_[timestamp] to ./archive directory
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
old_file_backup_path = os.path.join(directory, f"index.html_{timestamp}")
shutil.move(old_file_path, old_file_backup_path)
shutil.move(new_file_path, old_file_path)
archive_directory = "./archive"
shutil.copy(old_file_backup_path, os.path.join(archive_directory, f"index.html_{timestamp}"))

# Step 5: Log steps taken into ./log directory with a timestamped file
log_directory = "./log"
log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_file_path = os.path.join(log_directory, log_filename)
with open(log_file_path, "w") as f:
    f.write(f"NewFile: {new_file}\n")
    f.write(f"OldFile: {os.path.basename(old_file_path)}\n")
    f.write(f"OldFile backup: {os.path.basename(old_file_backup_path)}\n")
    f.write(f"Archive: {os.path.basename(old_file_backup_path)}\n")
    f.write(f"Timestamp: {timestamp}\n")
print("Done")

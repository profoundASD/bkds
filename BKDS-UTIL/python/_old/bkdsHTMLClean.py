import os
import shutil
from datetime import datetime
from bs4 import BeautifulSoup

# Set the path to the directory containing the HTML files
html_folder = '/home/aimless/BKDS-WEB-APP-01/bkds/web/html/main'
print('pre loop')

# Loop through each HTML file in the folder and its subdirectories
for root, dirs, files in os.walk(html_folder):
    print('looping0')
    for file_name in files:
        print('looping1')
        if file_name.endswith('.html'):
            # Get the full path of the HTML file
            file_path = os.path.join(root, file_name)

            # Open the HTML file and read the content
            with open(file_path, 'r') as f:
                html_content = f.read()

            # Parse the HTML content using Beautiful Soup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Modify the HTML here using Beautiful Soup methods
            # For example, you can remove all the <script> tags:
            for script_tag in soup.find_all('script'):
                script_tag.decompose()

            # Get the timestamp for the new file name
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            # Rename the original file to .html_old_[timestamp]
            old_file_name = f'{file_name.split(".")[0]}_old_{timestamp}.html'
            old_file_path = os.path.join(root, old_file_name)
            shutil.move(file_path, old_file_path)

            # Save the modified HTML content to the original file name
            with open(file_path, 'w') as f:
                f.write(str(soup))

import os
import json
import re

def parse_html_file(file_path):
    print('Parsing:', file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Use regex to handle variations in the $BEGIN and $END tags
    blocks = re.split(r'<!--\s*\$BEGIN POST BLOCK\s*-->', content)
    insights = []

    for block in blocks[1:]:  # Skip the first split part
        end_index = re.search(r'<!--\s*\$END POST BLOCK\s*-->', block)
        if end_index:
            block_content = block[:end_index.start()]

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(block_content, 'html.parser')


            insight = {
                "id": "INSIGHT",  # Placeholder
                "type": "PLACE_INSIGHT",  # Default type
                "insightDOMTarget": "main-content-feed",
                "contentPath": "/html/insights/bkds_proto_PlaceInsight.html",
                "insightBadge": "earth",
                "insightThumb": "earth",
                "insightSubject": soup.find('div', {'data-id': 'post-subj'}).text.strip(),
                "contentActive": True,
                "insightDOM_ID": "text-description",  # Placeholder
                "cssPath": "/css/bkds_rocket_launch_insight.css",  # Example path
                "filterCategory": os.path.basename(file_path).replace('.html', ''),
                "searchTerms": ["rockets", "launch", "rocket launch"],  # Example terms
                "imgStyle": "rocket-post-thumb-container"  # Example style
            }
            insights.append(insight)

    return insights

def generate_json_from_html_files(directory_path):
    all_insights = []

    for filename in os.listdir(directory_path):
        print('Processing file:', filename)
        if filename.endswith('.html'):
            file_path = os.path.join(directory_path, filename)
            insights = parse_html_file(file_path)
            all_insights.extend(insights)

    with open('output_bkdsContentGenHTMLExtract.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_insights, json_file, indent=4)

# Replace '/path/to/html/files' with the actual directory path

generate_json_from_html_files('/home/aimless76/Documents/Sync/BKDS/BKDS-APP/BKDS-WEB-APP/bkds/web/html/feeds')

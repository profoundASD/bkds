import requests
from bs4 import BeautifulSoup
import json

def wiki_template(title, wiki_url, wiki_photo):
    return f"""
    <!--BEGIN POST BLOCK -->
    <div style="margin-top:2%; border-width:2px;">
        <div class="monitored_post expanded post_container box" style="padding-bottom:2%; float:left;">
            <div class="top_post_section">
                <div class="user" id="iconUser1Image" style="background-image: url('../../image/Wiki.jpg'); float:left;">
                </div>
                <div class="post-text-box" style="font-size: 1.5em; background-color:#D3D3D3; color:#1F1F1F; height:80px; padding-bottom:3%; text-align:right;">
                    <div style="padding-right:5%; padding-top:5%;">
                    {title}
                    </div>
                </div>
            </div>
            <div class="bottom_post_section">
                <a href="{wiki_url}">
                    <div class="container" style="border-radius:3%;">
                    <img height=155px; width=245px; src="https:{wiki_photo}" >
                    </a>
                </div>
            </div>
        </div>
    </div>
    <!--END POST BLOCK -->
    """




def get_wiki(keyword):
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch={keyword}"
    response = requests.get(url)
    data = response.json()
    print('data ', data)

    file_path = '../data/output/bkds_wiki_search_out.json'  # Update file path for compatibility with this environment

    with open(file_path, 'w') as file:
        # Update: Write data as a JSON formatted string
        json.dump(data, file, indent=4)

    results = data['query']['search'][:8]  # Limit to first 8 results
    return [{'title': result['title'], 'wiki_url': f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"} for result in results]


def get_first_wikipedia_photo(wiki_url):
    response = requests.get(wiki_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        image_tags = soup.find_all('img')

        for image_tag in image_tags:
            src = image_tag.get('src', '').upper()
            alt_text = image_tag.get('alt', '').upper()
            parent_html = str(image_tag.parent).upper()

            if (not src.endswith('.OGG') and
                'PROTECTED' not in src and 'PROTECTION' not in src and
                'PENDING' not in src and 'FEATURED' not in src and
                'LISTEN' not in src and 'SYMBOL' not in src and
                'QUESTION_BOOK' not in src and 'WIKI_LETTER' not in src and
                'TEXT_DOCUMENT' not in src and 'QUESTION_MARK' not in src and
                'EMBLEM-MONEY' not in src and 'RED_PENCIL' not in src and
                'CENTRALAUTOLOGIN' not in src and ':' in parent_html and
                'PORTAL:TECHNOLOGY' not in parent_html and
                'FEATURED' not in alt_text and 'LISTEN' not in alt_text and
                'ICON' not in alt_text):

                # Extract the highest resolution image from srcset
                srcset = image_tag.get('srcset', '')
                if srcset:
                    srcset_parts = srcset.split(',')
                    highest_res_image = srcset_parts[-1].split(' ')[0].strip()
                    if highest_res_image and 'undefined' not in highest_res_image:
                        return highest_res_image

                # If no srcset or valid image in srcset, use the src attribute
                if src and 'undefined' not in src and 'STATIC' not in src:
                    return src

    return ''  # Return an empty string if no valid photo is found or an error occurs


def main():
    with open('../data/subjects/bkds_subjects.json', 'r') as file:
        keywords = json.load(file)

    html_output = ""
    for keyword in keywords:
        results = get_wiki(keyword['keyword'])
        for result in results:
            wiki_photo = get_first_wikipedia_photo(result['wiki_url'])
            html_output += wiki_template(result['title'], result['wiki_url'], wiki_photo)

    with open('../data/output/bkds_GetWikiOutput.html', 'w') as file:
        file.write(html_output)

if __name__ == "__main__":
    main()

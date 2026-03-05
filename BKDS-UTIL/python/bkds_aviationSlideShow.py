import os
import json
from bkds_Utilities import log_msg
import random

program_name = "SLIDESHOW_GEN"

def logMsg(msg):
    log_msg(program_name, 'BKDS_AVIATION_SLIDESHOW_GEN', msg)
    print(msg)

# Modify these as needed
INPUT_JSON_FILE = "/home/aimless76/Documents/Sync/BKDS/BKDS-APP-DEV/BKDS-NODEJS/public/data/images/master_image_aviation_index.json"

def load_json_data(json_file):
    """Load the JSON array from the provided file."""
    logMsg(f"Loading JSON data from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logMsg(f"Loaded {len(data)} images from JSON.")
    return data

def prepend_home_directory(image_path):
    """Prepend the user's home directory to the given image path."""
    home_dir = os.path.expanduser('~')
    home_dir = os.path.join(home_dir, 'Documents', 'Sync', 'BKDS', 'BKDS-APP-DEV', 'BKDS-NODEJS', 'public')
    normalized_path = image_path.lstrip('/')
    full_path = os.path.join(home_dir, normalized_path)
    return full_path

def deduplicate_images(json_data):
    """Deduplicate images and return a list of tuples (image_path, image_title)."""
    logMsg("Deduplicating images...")
    seen = set()
    unique_images = []
    for item in json_data:
        full_path = prepend_home_directory(item["img_url"])
        title = item["img_title"]
        if full_path not in seen and os.path.exists(full_path):
            seen.add(full_path)
            unique_images.append((full_path, title))
    logMsg(f"Found {len(unique_images)} unique images after deduplication.")
    return unique_images

def create_html_slideshow(unique_images, output_file="index.html"):
    """
    Generate an HTML file with embedded JavaScript to:
    - Display a random image at 70% width and height of the screen, centered.
    - On first click: show the title centered below the image without shifting the image.
    - On second click: load a new random image and hide the title.
    """

    # Convert Python list to JSON array for JS
    # We'll store objects with {src: "...", title: "..."}
    image_data = [{"src": img, "title": ttl} for (img, ttl) in unique_images]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Image Slideshow</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    background: #222;
    color: #fff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    overflow: hidden; /* Prevent scrolling */
    font-family: sans-serif;
  }}
  #container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-height: 70vh;
    max-width: 70vw;
    position: relative;
  }}
  img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    display: block;
    margin: auto;
  }}
  #title {{
    margin-top: 10px;
    font-size: 1.5em;
    text-align: center;
    visibility: hidden; /* hidden by default */
  }}
</style>
</head>
<body>

<div id="container">
  <img id="image" src="" alt="Image" />
  <div id="title"></div>
</div>

<script>
  const images = {json.dumps(image_data)};
  let currentImage = null;
  let titleVisible = false;

  function loadRandomImage() {{
    const randomIndex = Math.floor(Math.random() * images.length);
    currentImage = images[randomIndex];
    const img = document.getElementById('image');
    const titleDiv = document.getElementById('title');
    img.src = currentImage.src;
    titleDiv.textContent = currentImage.title;
    titleDiv.style.visibility = 'hidden';
    titleVisible = false;
  }}

  document.addEventListener('DOMContentLoaded', () => {{
    loadRandomImage();

    const container = document.getElementById('container');
    container.addEventListener('click', () => {{
      const titleDiv = document.getElementById('title');
      if (!titleVisible) {{
        // First click: show title
        titleDiv.style.visibility = 'visible';
        titleVisible = true;
      }} else {{
        // Second click: load new image
        loadRandomImage();
      }}
    }});
  }});
</script>

</body>
</html>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logMsg(f"HTML slideshow saved to {output_file}")

def main():
    logMsg("img processing started")
    data = load_json_data(INPUT_JSON_FILE)
    logMsg(f"json loaded: {INPUT_JSON_FILE}")
    unique_images = deduplicate_images(data)
    logMsg(f"got unique_images: {len(unique_images)} images")
    create_html_slideshow(unique_images, "index.html")
    logMsg("Process completed successfully. Open index.html in a browser to view slideshow.")

if __name__ == "__main__":
    main()

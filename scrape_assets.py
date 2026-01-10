import os
import re
import urllib.request
from urllib.parse import urljoin, urlparse

# Configuration
BASE_URL = "https://www.anantawealth.com"
INPUT_FILE = "original_index.html"
OUTPUT_FILE = "index.html"
ASSET_DIRS = {
    "css": "css",
    "js": "js",
    "image": "images",
    "font": "fonts"
}

# Create directories
for dir_name in ASSET_DIRS.values():
    os.makedirs(dir_name, exist_ok=True)

def download_file(url, folder, default_ext=""):
    try:
        # Handle protocol-relative URLs
        if url.startswith("//"):
            url = "https:" + url
        
        # Absolute URL
        full_url = urljoin(BASE_URL, url)
        
        # Parse filename
        parsed = urlparse(full_url)
        path = parsed.path
        filename = os.path.basename(path)
        
        # Handle query parameters in filename (e.g. style.css?ver=1.0)
        # We want to keep unique versions to avoid conflicts, or just strip query?
        # Let's keep the filename simple but unique enough.
        
        if not filename or filename == "":
            return url 
            
        # Basic cleaning of filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        if not os.path.splitext(filename)[1] and default_ext:
            filename += default_ext

        local_path = os.path.join(folder, filename)
        
        if os.path.exists(local_path):
            # print(f"Skipping existing: {filename}")
            return f"{folder}/{filename}"

        print(f"Downloading: {full_url} -> {local_path}")
        
        req = urllib.request.Request(
            full_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response, open(local_path, 'wb') as out_file:
            out_file.write(response.read())
            
        return f"{folder}/{filename}"
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return url 

def process_html():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex patterns for finding assets
    # These are simplified and might miss some edge cases but should cover most WP sites.
    
    # 1. CSS Links: <link ... href="...">
    def replace_css(match):
        full_tag = match.group(0)
        href_match = re.search(r'href=["\']([^"\']+)["\']', full_tag)
        if href_match:
            original_url = href_match.group(1)
            # Filter for CSS or image-like things typical in link tags
            if ".css" in original_url or "rel='stylesheet'" in full_tag or 'rel="stylesheet"' in full_tag:
                 new_path = download_file(original_url, ASSET_DIRS["css"], ".css")
                 return full_tag.replace(original_url, new_path)
        return full_tag

    content = re.sub(r'<link[^>]+>', replace_css, content)

    # 2. Scripts: <script ... src="...">
    def replace_script(match):
        full_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag)
        if src_match:
            original_url = src_match.group(1)
            new_path = download_file(original_url, ASSET_DIRS["js"], ".js")
            return full_tag.replace(original_url, new_path)
        return full_tag

    content = re.sub(r'<script[^>]+>', replace_script, content)
    
    # 3. Images: <img ... src="...">
    def replace_img(match):
        full_tag = match.group(0)
        
        # Remove srcset if present to force browser to use src (simpler for replication)
        full_tag = re.sub(r'srcset=["\'][^"\']+["\']', '', full_tag)
        
        src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag)
        if src_match:
            original_url = src_match.group(1)
            if not original_url.startswith("data:"): # Skip data URIs
                new_path = download_file(original_url, ASSET_DIRS["image"])
                return full_tag.replace(original_url, new_path)
        return full_tag
        
    content = re.sub(r'<img[^>]+>', replace_img, content)

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_html()

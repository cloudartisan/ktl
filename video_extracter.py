import json
import time
import argparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from login import login

def sanitize_path(path):
    return path.replace(">", "/").replace(":", "-").replace("?", "").strip()

def sanitize_filename(title):
    return "".join(c for c in title if c.isalnum() or c in " ._-()").rstrip()

def extract_download_url(driver, video_url):
    try:
        driver.get(video_url)

        # Wait for the iframe element to load
        iframe_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        # Extract the src attribute of the iframe
        iframe_src = iframe_element.get_attribute("src")
        if "vimeo.com" in iframe_src:
            print(f"Embedded Vimeo URL found: {iframe_src}")
            return iframe_src
        else:
            print(f"No Vimeo URL found on page: {video_url}")
            return None
    except Exception as e:
        print(f"Error extracting download URL from {video_url}: {e}")
        return None

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Load videos and extract Vimeo URLs.")
    parser.add_argument("--email", required=True, help="Email for login")
    parser.add_argument("--password", required=True, help="Password for login")
    args = parser.parse_args()

    with open("crawled.json", "r") as f:
        all_videos = json.load(f)

    driver = webdriver.Chrome()
    login(driver, args.email, args.password)

    # Load processed videos if exists
    try:
        with open("extracted.json", "r") as f:
            processed_videos = json.load(f)
            processed_urls = {video["embed_page_url"] for video in processed_videos}
    except FileNotFoundError:
        processed_videos = []
        processed_urls = set()

    # Process all videos
    download_links = []
    for video in all_videos:
        title = video.get("title", "Unknown Title")
        url = video.get("url")
        path = video.get("path", "")

        if url in processed_urls:
            print(f"Skipping already processed video: {title} - {url}")
            continue

        print(f"Processing video: {title} - {url}")

        download_url = extract_download_url(driver, url)
        if download_url:
            sanitized_path = sanitize_path(path)
            sanitized_title = sanitize_filename(title)
            output_path = f"{sanitized_path}/{sanitized_title}.mp4"
            download_links.append({
                "title": title,
                "embed_page_url": url,
                "vimeo_url": download_url,
                "output_path": output_path
            })

    # Merge new links with previously processed videos
    download_links.extend(processed_videos)

    # Save download links to a JSON file
    with open("extracted.json", "w") as f:
        json.dump(download_links, f, indent=4)

    print(f"Saved {len(download_links)} download links to extracted.json")

    driver.quit()

if __name__ == "__main__":
    main()
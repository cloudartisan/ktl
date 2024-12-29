# Kojo Trick Lab Local Backup Tools

## Overview
This project consists of three Python scripts designed to help back up videos from Kojo Trick Lab to your local machine for personal use during training sessions. The tools allow you to crawl the video library, extract video download links, and fetch the videos while maintaining their directory structure.

### Disclaimer
**This project was created solely for personal backup purposes. Under no circumstances should this project be used to violate copyright law or distribute the content without permission. Respect the rights of content creators and ensure all usage complies with applicable laws and the terms of service of the website.**

## Scripts
### 1. `video_crawler.py`
Crawls the Kojo Trick Lab website and identifies all videos available in the library.

- **Input:** None (scrapes directly from the website).
- **Output:** `crawled.json` containing metadata and structure of the video library.

### 2. `video_extracter.py`
Extracts video metadata and download URLs from the crawled data.

- **Input:** `crawled.json`
- **Output:** `extracted.json` containing video titles, embed page URLs, and video download URLs.

### 3. `video_fetcher.py`
Fetches and downloads the videos locally, ensuring proper directory structure and tracking completed downloads.

- **Input:** `extracted.json`
- **Output:** Downloads videos to the specified directory and creates `fetched.json` to track completed downloads.

## Files
- **`crawled.json`**: Metadata of videos available in the library.
- **`extracted.json`**: Video titles, embed page URLs, and video download URLs.
- **`fetched.json`**: Tracks completed downloads, including metadata such as file size and timestamp.

## Prerequisites
1. Install Python 3.6 or later.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video downloads.

## Usage
### 1. Crawling Videos
Run the crawler script to gather video metadata:
```bash
python video_crawler.py --email <your-email> --password <your-password>
```

### 2. Extracting Video Links
Run the extractor script to generate download links:
```bash
python video_extracter.py --email <your-email> --password <your-password>
```

### 3. Downloading Videos
Run the fetcher script to download videos locally:
```bash
python video_fetcher.py --path <download-directory>
```
- Use the `--force` option to re-download videos even if they are already downloaded.

## Important Notes
- **Respect Copyright**: These tools are for personal backup purposes only. Do not use them to violate copyright law or share/download content without proper authorisation.
- **Video Access**: Ensure you have access to the videos on the Kojo Trick Lab platform before attempting to back them up.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

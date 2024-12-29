import argparse
import json
import os
import subprocess
import shutil

def check_yt_dlp():
    """Check if yt-dlp is installed and available in PATH."""
    if shutil.which("yt-dlp") is None:
        print("Error: yt-dlp is not installed or not found in PATH. Please install yt-dlp to proceed.")
        exit(1)

def download_video(video, output_directory):
    """Download a video using yt-dlp."""
    title = video["title"]
    url = video["vimeo_url"]
    referer = video["embed_page_url"]

    # Construct the output path
    video_path = os.path.join(output_directory, *video["path"].split("/"))
    os.makedirs(video_path, exist_ok=True)

    output_file = os.path.join(video_path, f"{title}.mp4")

    if os.path.exists(output_file):
        print(f"Skipping {title}, already downloaded.")
        return

    # Use yt-dlp to download the video
    command = [
        "yt-dlp",
        "--referer",
        referer,
        "--output",
        output_file,
        url
    ]

    print(f"Downloading {title} from {url}...")
    try:
        subprocess.run(command, check=True)
        print(f"Downloaded: {title}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {title}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download videos from Kojo Trick Lab using a JSON file.")
    parser.add_argument("--input", required=True, help="Path to the input JSON file containing video links.")
    parser.add_argument("--output", required=True, help="Directory to save downloaded videos.")
    args = parser.parse_args()

    # Check for yt-dlp
    check_yt_dlp()

    # Load video data from JSON
    with open(args.input, "r") as f:
        videos = json.load(f)

    # Download each video
    for video in videos:
        download_video(video, args.output)

if __name__ == "__main__":
    main()
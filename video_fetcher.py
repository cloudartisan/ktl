import argparse
import json
import os
import subprocess
import shutil
from datetime import datetime

def check_yt_dlp():
    """Check if yt-dlp is installed and accessible in the PATH."""
    if shutil.which("yt-dlp") is None:
        print("Error: yt-dlp is not installed or not found in PATH. Please install yt-dlp to proceed.")
        exit(1)

def load_fetched_videos(fetched_file):
    """Load the fetched videos metadata from the specified JSON file.

    Args:
        fetched_file (str): Path to the JSON file containing fetched videos metadata.

    Returns:
        dict: Dictionary containing metadata of fetched videos.
    """
    if os.path.exists(fetched_file):
        with open(fetched_file, "r") as f:
            return json.load(f)
    return {}

def save_fetched_videos(fetched_file, fetched_data):
    """Save the fetched videos metadata to the specified JSON file.

    Args:
        fetched_file (str): Path to the JSON file to save metadata.
        fetched_data (dict): Dictionary containing metadata of fetched videos.
    """
    with open(fetched_file, "w") as f:
        json.dump(fetched_data, f, indent=4)

def is_video_fetched(video, fetched_data, output_file):
    """Check if a video has already been fetched based on metadata and file existence.

    Args:
        video (dict): Metadata of the video to check.
        fetched_data (dict): Dictionary of fetched videos metadata.
        output_file (str): Path to the expected video file.

    Returns:
        bool: True if the video is already fetched; False otherwise.
    """
    if video["vimeo_url"] in fetched_data:
        return True
    return os.path.exists(output_file) and os.path.getsize(output_file) > 0

def download_video(video, output_directory, fetched_file, fetched_data, force):
    """Download a video using yt-dlp and update the fetched metadata on success.

    Args:
        video (dict): Metadata of the video to download.
        output_directory (str): Directory where the video should be saved.
        fetched_file (str): Path to the JSON file storing fetched videos metadata.
        fetched_data (dict): Dictionary of fetched videos metadata.
        force (bool): Whether to force re-download the video.
    """
    title = video["title"]
    url = video["vimeo_url"]
    referer = video.get("embed_page_url", "")

    output_file = os.path.join(output_directory, video["output_path"])
    video_path = os.path.dirname(output_file)
    os.makedirs(video_path, exist_ok=True)

    if not force and is_video_fetched(video, fetched_data, output_file):
        print(f"Skipping {title}, already downloaded.")
        return

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
        if is_video_fetched(video, fetched_data, output_file):
            print(f"Downloaded: {title}")
            fetched_data[url] = {
                "title": title,
                "output_path": video["output_path"],
                "embed_page_url": referer,
                "file_size": os.path.getsize(output_file),
                "timestamp": datetime.now().isoformat()
            }
            save_fetched_videos(fetched_file, fetched_data)
        else:
            print(f"Error: {title} did not download correctly.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {title}: {e}")

def main():
    """Main function to parse arguments and initiate the video downloading process."""
    parser = argparse.ArgumentParser(description="Download videos from Kojo Trick Lab using a JSON file.")
    parser.add_argument("--path", required=True, help="Directory to save downloaded videos.")
    parser.add_argument("--force", action="store_true", help="Force re-download videos even if already fetched.")
    args = parser.parse_args()

    input_file = "extracted.json"
    fetched_file = "fetched.json"

    check_yt_dlp()

    with open(input_file, "r") as f:
        videos = json.load(f)

    fetched_data = load_fetched_videos(fetched_file)

    for video in videos:
        download_video(video, args.path, fetched_file, fetched_data, args.force)

if __name__ == "__main__":
    main()
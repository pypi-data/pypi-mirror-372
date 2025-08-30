#!/usr/bin/env python3
# smd/downloader.py

# -----------------------------------------
# Social Media Downloader
# Version: 1.1.11
# Author: Nayan Das
# License: MIT
# Description: A command-line tool to download videos from various social media platforms like YouTube, TikTok, Facebook, Instagram, X & more.
# It supports instagram batch downloads, format selection, and maintains a download history.
# Dependencies: yt-dlp, instaloader, requests, tqdm, pyfiglet, termcolor
# Usage: pip install social-media-downloader
# Requirements: Python 3.10+
# Note: Ensure FFmpeg is installed and added to your PATH for audio extraction.
# Last Updated: 18th June 2025
# -----------------------------------------

import os
import sys
import csv
import time
import json
import shutil
import yt_dlp
import logging
import tempfile
import requests
import subprocess
import instaloader
from tqdm import tqdm
from pyfiglet import Figlet
from termcolor import colored
from datetime import datetime
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------
# Version and Update Variables
# ---------------------------------
AUTHOR = "Nayan Das"
CURRENT_VERSION = "1.1.11"
EMAIL = "nayanchandradas@hotmail.com"
DISCORD_INVITE = "https://discord.gg/skHyssu"
WEBSITE = "https://nayandas69.github.io/Social-Media-Downloader"
GITHUB_REPO_URL = "https://github.com/nayandas69/Social-Media-Downloader"
PYPI_API_URL = "https://pypi.org/pypi/social-media-downloader/json"


# ---------------------------------
# Author Details Display
# ---------------------------------
def display_author_details():
    """Display the animated banner and author details."""

    # Clear screen
    os.system("cls" if os.name == "nt" else "clear")

    # Fancy fonts
    banner_font = Figlet(font="slant")

    # Render text
    banner_text = banner_font.renderText("Social Media Downloader")

    # Color them
    banner_colored = colored(banner_text, "cyan", attrs=["bold"])

    # Animate banner
    for line in banner_colored.splitlines():
        print(line)
        time.sleep(0.05)

    print("\n")

    # Author Info Animated
    info_lines = [
        (f"Author   : ", AUTHOR, "yellow", "white"),
        (f"Email    : ", EMAIL, "yellow", "cyan"),
        (f"Discord  : ", DISCORD_INVITE, "yellow", "cyan"),
        (f"Repo     : ", GITHUB_REPO_URL, "yellow", "cyan"),
        (f"Website  : ", WEBSITE, "yellow", "cyan"),
        (f"Version  : ", CURRENT_VERSION, "yellow", "green"),
    ]

    for label, value, label_color, value_color in info_lines:
        print(
            colored(f"{label:<10}", label_color, attrs=["bold"])
            + colored(value, value_color)
        )
        time.sleep(0.2)

    # Loader animation
    print(colored("\nLoading", "yellow", attrs=["bold"]), end="", flush=True)
    for _ in range(5):
        time.sleep(0.4)
        print(colored(".", "yellow", attrs=["bold"]), end="", flush=True)

    time.sleep(0.5)

    print()  # Final line break


display_author_details()


# ---------------------------------
# Logging Setup
# ---------------------------------
logging.basicConfig(
    filename="downloader.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------------------------
# Load Configuration
# ---------------------------------
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "default_format": "show_all",  # Can be: 'show_all', 'mp3', '720p', '1080p', etc.
    "download_directory": "media",
    "history_file": "download_history.csv",
    "mp3_quality": "192",  # Supported: 64, 128, 192, 256, 320, 396
}

VALID_DEFAULT_FORMATS = {
    "show_all",
    "mp3",
    "360p",
    "480p",
    "720p",
    "1080p",
    "1440p",
    "2160p",
    "4320p",
}
VALID_MP3_QUALITIES = {"64", "128", "192", "256", "320", "396"}


def load_config():
    """Load, validate, and auto-correct the configuration file."""
    config_changed = False

    # If config file does not exist, create it with default config
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logging.info(f"Created new config file with defaults: {CONFIG_FILE}")
        return DEFAULT_CONFIG

    # Load existing config
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Failed to load config file: {e}. Resetting to defaults.")
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    # Add missing keys from default
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in config_data:
            logging.warning(
                f"Missing '{key}' in config. Setting to default: {default_value}"
            )
            config_data[key] = default_value
            config_changed = True

    # Validate mp3_quality
    mp3_quality = str(config_data.get("mp3_quality", "192"))
    if mp3_quality not in VALID_MP3_QUALITIES:
        logging.warning(f"Invalid mp3_quality '{mp3_quality}', resetting to '192'.")
        config_data["mp3_quality"] = "192"
        config_changed = True

    # Validate default_format
    default_format = str(config_data.get("default_format", "show_all")).lower()
    if default_format not in VALID_DEFAULT_FORMATS:
        logging.warning(
            f"Invalid default_format '{default_format}', resetting to 'show_all'."
        )
        config_data["default_format"] = "show_all"
        config_changed = True

    # Save updated config if changes were made
    if config_changed:
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f, indent=4)
            logging.info("Config file updated with corrected values.")
        except IOError as e:
            logging.error(f"Failed to write corrected config: {e}")

    return config_data


# Load config and extract validated values
config = load_config()

# Assign global variables
download_directory = config.get("download_directory", "media")
history_file = config.get("history_file", "download_history.csv")
mp3_quality = str(config.get("mp3_quality", "192"))
default_format = config.get("default_format", "show_all")

# Ensure download directory exists
try:
    os.makedirs(download_directory, exist_ok=True)
except OSError as e:
    logging.error(f"Failed to create download directory '{download_directory}': {e}")
    raise SystemExit("Cannot proceed without a valid download directory.")


# ---------------------------------
# Check for FFmpeg
# ---------------------------------
def ensure_ffmpeg():
    """Ensure that FFmpeg is installed before proceeding."""
    if shutil.which("ffmpeg") is None:
        print(
            "\033[1;31m\nFFmpeg is not installed. Please install FFmpeg and try again.\033[0m"
        )
        print("\033[1;31mDownload FFmpeg from: https://ffmpeg.org/download.html\033[0m")
        print("\033[1;31mFor Windows users, add FFmpeg to your PATH.\033[0m")
        print("\033[1;31mFor Linux users, run: sudo apt install ffmpeg\033[0m")
        print("\033[1;31mAfter installation, restart the program.\033[0m")
        sys.exit(1)
    else:
        print("\033[1;32mFFmpeg is installed. Proceeding...\033[0m")


# ---------------------------------
# Check for Updates
# ---------------------------------
def check_for_updates():
    """Check for updates from PyPI and notify users."""
    if not check_internet_connection():
        print("\n\033[1;31mNo internet connection. Please connect and try again.\033[0m")
        return

    print(f"\n\033[1;36mChecking for updates...\033[0m")
    print(f"\033[1;33mCurrent version:\033[0m {CURRENT_VERSION}")

    try:
        # Make request to PyPI API with timeout
        response = requests.get(PYPI_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract latest version from PyPI response
        latest_version = data.get("info", {}).get("version", "Unknown")

        def parse_version(version_str):
            """Parse version string into tuple of integers for comparison."""
            try:
                clean_version = str(version_str).strip()
                return tuple(map(int, clean_version.split('.')))
            except (ValueError, AttributeError, TypeError):
                return (0, 0, 0)

        current_parsed = parse_version(CURRENT_VERSION)
        latest_parsed = parse_version(latest_version)

        print(f"\033[1;33mLatest version:\033[0m {latest_version}")

        if latest_parsed > current_parsed:
            print(f"\n\033[1;32m New version available: {latest_version}\033[0m")
            print(f"\n\033[1;36mUpdate options:\033[0m")
            print(f"\033[1;33m1. Using pip:\033[0m")
            print(f"   \033[1;32mpip install social-media-downloader --upgrade\033[0m")
            print(f"\n\033[1;33m2. Download from GitHub:\033[0m")
            print(f"   {GITHUB_REPO_URL}/releases/latest")
            
            # Show release info if available
            release_info = data.get("info", {})
            summary = release_info.get("summary", "")
            if summary:
                print(f"\n\033[1;36mWhat's new:\033[0m {summary}")

        elif latest_parsed == current_parsed:
            print(f"\n\033[1;32m You're up to date!\033[0m")
            print(f"\033[1;36mJoin our Discord for updates and support:\033[0m")
            print(f"{DISCORD_INVITE}")
        else:
            print(f"\n\033[1;33m  You're running a newer version than what's published on PyPI.\033[0m")
            print(f"\033[1;36mThis might be a development or beta version.\033[0m")

    except requests.exceptions.Timeout:
        print(f"\n\033[1;31m Request timed out. Please check your internet connection and try again.\033[0m")
        logging.error("Update check timed out")
    except requests.exceptions.RequestException as e:
        print(f"\n\033[1;31m Error checking for updates: {e}\033[0m")
        print(f"\033[1;36mYou can manually check for updates at:\033[0m {GITHUB_REPO_URL}/releases")
        logging.error(f"Update check failed: {e}")
    except (KeyError, TypeError) as e:
        print(f"\n\033[1;31m Error parsing update information: {e}\033[0m")
        print(f"\033[1;36mYou can manually check for updates at:\033[0m {GITHUB_REPO_URL}/releases")
        logging.error(f"Update parsing failed: {e}")
    except Exception as e:
        print(f"\n\033[1;31m Unexpected error during update check: {e}\033[0m")
        logging.error(f"Unexpected update check error: {e}", exc_info=True)


# ---------------------------------
# Utility Functions
# ---------------------------------
def check_internet_connection():
    """Check if the system has an active internet connection."""
    try:
        requests.head("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def ensure_internet_connection():
    """Ensure that an internet connection is active before proceeding."""
    while not check_internet_connection():
        print("\033[91m\nNo internet connection. Retrying in 5 seconds...\033[0m")
        time.sleep(5)
    print("\033[92mInternet connection detected. Proceeding...\033[0m")


def log_download(url, status):
    """Log the download status in history and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_file, "a+", newline="") as f:
        csv.writer(f).writerow([url, status, timestamp])
    logging.info(f"Download status for {url}: {status}")


def get_unique_filename(filename):
    """Ensure downloaded files are renamed if duplicates exist."""
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filename):
        filename = f"{base} ({counter}){ext}"
        counter += 1
    return filename


# -------------------------------------
# Validate URLs for Supported Platforms
# -------------------------------------
def is_valid_platform_url(url, allowed_domains):
    """Check if the URL matches one of the allowed domains."""
    return any(domain in url for domain in allowed_domains)


# ----------------------------------
# Format Table for Available Formats
# ----------------------------------
def print_format_table(info):
    formats = info.get("formats", [])
    table_data = []

    for fmt in formats:
        # Skip non-downloadable formats like storyboards
        if fmt.get("vcodec") == "none" and fmt.get("acodec") == "none":
            continue

        fmt_id = fmt.get("format_id")
        ext = fmt.get("ext")
        resolution = (
            f"{fmt.get('width', '')}x{fmt.get('height', '')}"
            if fmt.get("height")
            else "audio"
        )
        fps = fmt.get("fps", "")
        filesize = fmt.get("filesize", 0)
        filesize_str = f"{filesize / (1024 * 1024):.2f} MB" if filesize else "-"
        vcodec = fmt.get("vcodec", "")
        acodec = fmt.get("acodec", "")
        note = fmt.get("format_note", "")

        # Add color to the format_id column (Green)
        fmt_id_colored = f"\033[1;32m{fmt_id}\033[0m"  # Green

        table_data.append(
            [fmt_id_colored, ext, resolution, fps, filesize_str, vcodec, acodec, note]
        )

    # Apply yellow color to all the headers dynamically
    headers = [
        f"\033[1;33m{header}\033[0m"
        for header in [
            "ID",
            "EXT",
            "RESOLUTION",
            "FPS",
            "SIZE",
            "VCODEC",
            "ACODEC",
            "NOTE",
        ]
    ]
    print("\n\033[1;36mAvailable formats:\033[0m")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# -----------------------------------------------------------
# Download Functions for Youtube, TikTok and other platforms
# -----------------------------------------------------------
def download_youtube_or_tiktok_video(url):
    """Download a video using a format from config or prompt user if set to 'show_all'."""

    # Validate URL against allowed domains
    allowed_domains = [
        "youtube.com",
        "youtu.be",
        "tiktok.com",
        "facebook.com",
        "fb.watch",
        "x.com",
        "twitter.com",
        "twitch.tv",
        "clips.twitch.tv",
        "snapchat.com",
        "reddit.com",
        "packaged-media.redd.it",
        "vimeo.com",
        "streamable.com",
        "pinterest.com",
        "pin.it",
        "linkedin.com",
        "bilibili.tv",
        "odysee.com",
        "rumble.com",
        "gameclips.io",
        "triller.co",
        "snackvideo.com",
        "kwai.com",
        "imdb.com",
        "weibo.com",
        "dailymotion.com",
        "dai.ly",
        "tumblr.com",
        "bsky.app",
    ]

    if not is_valid_platform_url(url, allowed_domains):
        print("\n\033[1;31mInvalid URL. Please enter a valid URL.\033[0m")
        print(
            "\033[1;31mSupported platforms: https://nayandas69.github.io/Social-Media-Downloader/supported-platforms\033[0m"
        )
        return

    ensure_ffmpeg()
    ensure_internet_connection()

    try:
        # Extract video info first
        with yt_dlp.YoutubeDL({"listformats": False}) as ydl:
            info = ydl.extract_info(url, download=False)

        # Metadata display
        title = info.get("title", "Unknown Title")
        uploader = info.get("uploader", "Unknown Uploader")
        upload_date = info.get("upload_date", "Unknown Date")
        upload_date_formatted = (
            datetime.strptime(upload_date, "%Y%m%d").strftime("%B %d, %Y")
            if upload_date != "Unknown Date"
            else upload_date
        )

        print("\n\033[1;36mVideo Details:\033[0m")
        print(f"\033[1;33mTitle:\033[0m {title}")
        print(f"\033[1;33mUploader:\033[0m {uploader}")
        print(f"\033[1;33mUpload Date:\033[0m {upload_date_formatted}")

        # Prepare filename
        filename_base = get_unique_filename(
            os.path.join(download_directory, f"{title}")
        )

        # Mapping for user-friendly quality labels
        friendly_format_map = {
            "360p": "bestvideo[height<=360]+bestaudio/best",
            "480p": "bestvideo[height<=480]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "1440p": "bestvideo[height<=1440]+bestaudio/best",
            "2160p": "bestvideo[height<=2160]+bestaudio/best",
            "4320p": "bestvideo[height<=4320]+bestaudio/best",
            "mp3": "mp3",
            "best": "bestvideo+bestaudio/best",
        }

        # Determine format preference
        preferred_format = config.get("default_format", "show_all").lower()

        if preferred_format == "show_all":
            print_format_table(info)
            choice = input(
                "\nEnter format ID to download (or type 'mp3' for audio only): "
            ).strip()
        else:
            choice = friendly_format_map.get(preferred_format, preferred_format)

        # Handle mp3 download
        if choice == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(download_directory, f"{title}.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": config.get("mp3_quality", "192"),
                    }
                ],
            }

        else:
            # Check if selected format ID exists
            selected_fmt = next(
                (f for f in info.get("formats", []) if f.get("format_id") == choice),
                None,
            )

            # Auto-correct video-only downloads [Now fix with selected]
            if selected_fmt and selected_fmt.get("acodec") in ["none", None, ""]:
                print(
                    f"\n\033[1;33mNote:\033[0m Selected format '{choice}' has no audio."
                )
                print(
                    f"\033[1;32mAuto-fix:\033[0m Merging selected video ({choice}) with best available audio."
                )
                choice = f"{choice}+bestaudio"

            ydl_opts = {
                "format": choice,
                "outtmpl": f"{filename_base}.%(ext)s",
                "merge_output_format": "mp4",
                "noplaylist": True,
            }

        # Perform the download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            log_download(url, "Success")
            print(f"\n\033[1;32mDownloaded successfully:\033[0m {title}")

    except Exception as e:
        log_download(url, f"Failed: {str(e)}")
        logging.error(f"Error downloading video from {url}: {str(e)}", exc_info=True)
        print(f"\033[1;31mError downloading video:\033[0m {str(e)}")


# ---------------------------------
# Download Functions for Instagram
# ---------------------------------
def download_instagram_post(url):
    """Download an Instagram post."""
    allowed_domains = ["instagram.com"]
    if not is_valid_platform_url(url, allowed_domains):
        print("\n\033[1;31mInvalid URL. Please enter a valid Instagram URL.\033[0m")
        return
    ensure_internet_connection()
    try:
        L = instaloader.Instaloader()
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=download_directory)
        log_download(url, "Success")
        print(f"\n\033[1;32mDownloaded Instagram post from successfully:\033[0m {url}")
    except Exception as e:
        log_download(url, f"Failed: {str(e)}")
        logging.error(f"Instagram download error for {url}: {str(e)}")
        print(f"\033[1;31mError downloading video:\033[0m {str(e)}")


# ---------------------------------
# Extract MP3 from Instagram Video
# ---------------------------------
def extract_instagram_video_mp3(url):
    """Download Instagram video/reel and auto-convert to MP3."""
    allowed_domains = ["instagram.com"]
    if not is_valid_platform_url(url, allowed_domains):
        print(
            "\n\033[1;31mError: This feature only supports Instagram video URLs (reels, posts, TV).\033[0m"
        )
        log_download(url, "Failed: Invalid Instagram URL")
        return

    ensure_internet_connection()

    # Extract shortcode from supported Instagram URL types
    if "/reel/" in url:
        shortcode = url.split("/reel/")[1].split("/")[0]
    elif "/p/" in url:
        shortcode = url.split("/p/")[1].split("/")[0]
    elif "/tv/" in url:
        shortcode = url.split("/tv/")[1].split("/")[0]
    else:
        print(
            "\n\033[1;31mError: This feature only supports Instagram video URLs (reels, posts, TV).\033[0m"
        )
        print("\033[1;31mPlease provide a valid Instagram video URL.\033[0m")
        log_download(url, "Failed: Unsupported Instagram video URL")
        return

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = instaloader.Instaloader(
                dirname_pattern=temp_dir, save_metadata=False, download_comments=False
            )

            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            if not post.is_video:
                print("This post is not a video.")
                log_download(url, "Failed: Not a video post")
                return

            print("Downloading video...")
            loader.download_post(post, target=shortcode)

            # Find downloaded .mp4
            video_path = None
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        video_path = os.path.join(root, file)
                        break

            if not video_path or not os.path.exists(video_path):
                print("Video file not found.")
                log_download(url, "Failed: Video file not found after download")
                return

            ensure_ffmpeg()

            # Define MP3 path
            filename_base = f"instagram_{shortcode}"
            mp3_path = os.path.join(download_directory, f"{filename_base}.mp3")

            print("Extracting MP3...")
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    video_path,
                    "-vn",
                    "-ab",
                    f"{mp3_quality}k",
                    "-ar",
                    "44100",
                    "-y",
                    mp3_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            print(f"\n\033[1;32mDownloaded successfully:\033[0m {url}")
            log_download(url, f"Success: {url}")

    except Exception as e:
        print(f"\033[1;31mError: {e}\033[0m")
        log_download(url, f"Failed: {str(e)}")
        logging.error(f"Instagram MP3 extract error for {url}: {str(e)}")


# -------------------------
# Batch Download Instagram
# -------------------------
def batch_download_from_file(file_path):
    """Read URLs from a text file and download them concurrently."""
    ensure_internet_connection()
    print(f"Reading URLs from {file_path}...")

    # Read all lines and clean up empty lines
    with open(file_path, "r") as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]

    if not urls:
        print("No URLs found in the file.")
        return

    print("Starting batch download...")

    with ThreadPoolExecutor() as executor:
        list(
            tqdm(
                executor.map(download_instagram_post, urls),
                total=len(urls),
                desc="Instagram Batch",
            )
        )

    print("Download complete.")


# --------------------------------
# Help Menu
# --------------------------------
def show_help():
    """Display the help menu with usage instructions."""
    print("\n\033[1;36mHow to Use Social Media Downloader:\033[0m")
    print("1. \033[1;33mDownload Videos:\033[0m Enter '1' to download a public videos.")
    print(
        "2. \033[1;33mDownload Instagram Content:\033[0m Enter '2' to download a public Instagram post, video, reel, picture. And for Batch download provide a text file containing public Instagram post URLs."
    )
    print(
        "3. \033[1;33mCheck for Updates:\033[0m Enter '3' to check for software updates and install the latest version."
    )
    print("4. \033[1;33mHelp Menu:\033[0m Enter '4' to display this help guide.")
    print("5. \033[1;33mExit the Program:\033[0m Enter '5' to close the application.\n")

    print("\033[1;31mImportant Notice:\033[0m")
    print("\033[1;31mThis tool only supports downloading public videos.\033[0m")
    print(
        "\033[1;31mPrivate, restricted, or non-public content cannot be downloaded.\033[0m\n"
    )
    print("\033[1;32mSupported Platforms:\033[0m")
    print(
        "• Click here https://nayandas69.github.io/Social-Media-Downloader/supported-platforms\n"
    )

    print("\033[1;32mAdditional Information:\033[0m")
    print("• All downloaded files are saved in the 'media' directory.")
    print("• Download history and logs are automatically recorded for reference.")
    print(
        "• For support, feature requests, or bug reports, please contact the author below:\n"
    )
    print(f"\033[1;33mEmail: {EMAIL}\033[0m")
    print(f"\033[1;33mDiscord: {DISCORD_INVITE}\033[0m")
    print(f"\033[1;33mGitHub: {GITHUB_REPO_URL}\033[0m")
    print(f"\033[1;33mWebsite: {WEBSITE}\033[0m")


# ---------------------------------
# Instagram Menu with Options
# ---------------------------------
def instagram_menu():
    print("\nInstagram Menu")
    print("1. Download Reel, Video & Pictures")
    print("2. Extract MP3 from Instagram Video")
    print("3. Batch Download Instagram Posts")
    choice = input("Enter your choice: ")

    if choice == "1":
        url = input("Enter Instagram URL: ").strip()
        download_instagram_post(url)
    elif choice == "2":
        url = input("Enter video URL: ").strip()
        extract_instagram_video_mp3(url)
    elif choice == "3":
        file_path = input(
            "Enter the path to the text file containing Instagram URLs: "
        ).strip()
        if os.path.exists(file_path):
            batch_download_from_file(file_path)
        else:
            print(f"File not found: {file_path}")
            print(f"\033[1;31mFor Linux example: /home/user/batch_links.txt\033[0m")
            print(
                f"\033[1;31mFor Windows example: C:\\Users\\user\\batch_links.txt\033[0m"
            )
    else:
        print("Invalid choice.")


# ---------------------------------
# Main Function: CLI Interface
# ---------------------------------
def main():
    """Main function for user interaction."""
    try:
        input(
            "\nPress Enter to start the Social Media Downloader..."
        )  # Wait for user input before execution

        print(f"\033[38;2;255;105;180mWelcome to Social Media Downloader!\033[0m")

        while True:
            print("\n" + "─" * 60)
            print("\n1. Download YouTube/TikTok... etc.")
            print("2. Download Instagram")
            print("3. Check for updates")
            print("4. Help")
            print("5. Exit")

            choice = input("\nEnter your choice: ").strip()
            if not choice:
                continue  # skip empty input

            if choice == "1":
                url = input("Enter video URL: ").strip()
                download_youtube_or_tiktok_video(url)
            elif choice == "2":
                instagram_menu()
            elif choice == "3":
                check_for_updates()
            elif choice == "4":
                show_help()
            elif choice == "5":
                print(
                    f"\033[38;2;255;105;180mSocial Media Downloader has exited successfully. Thank you for using it!\033[0m"
                )

                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        logging.critical(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {e}")


def cli():
    main()

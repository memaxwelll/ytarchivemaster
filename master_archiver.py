import os
import subprocess
import time
import psutil
from threading import Thread
import re
from datetime import datetime

# Define the directories for each drive option
directories_map = {
    '1': 'D:\\YT',
    '2': 'E:\\YT',
    '3': 'F:\\YT'
}

# Function to prompt the user to select the drive
def get_drive_selection():
    print("Select the drive to update:")
    print("1 = D:\\YT")
    print("2 = E:\\YT")
    print("3 = F:\\YT")

    selection = input("Enter your choice (1, 2, 3): ").strip()

    if selection not in directories_map:
        print("Invalid input. Please enter 1, 2, or 3.")
        return get_drive_selection()  # Ask again if the input is invalid

    return selection

# Get the user's drive selection
selection = get_drive_selection()
drive_path = directories_map[selection]  # The selected drive's YT directory

# Path to ffmpeg on the chosen drive (assuming ffmpeg is in the same YT directory)
ffmpeg_path = os.path.join(drive_path, 'ffmpeg')

# Log file for yt-dlp output
log_file = 'yt-dlp.log'

# Purge the log file at the start of each run
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("")  # Clear the file by opening it in write mode

def log_output(line):
    """Log yt-dlp output to yt-dlp.log file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {line}\n")

def count_total_videos(drive_path):
    """Count the total number of videos in the library based on the downloaded video structure."""
    video_count = 0
    for root, dirs, files in os.walk(drive_path):
        for file in files:
            if file.endswith(".mp4"):  # Assuming videos are in MP4 format
                video_count += 1
    return video_count

# ANSI color codes for individual stats
COLOR_RESET = "\033[0m"
COLOR_TIME = "\033[94m"  # Blue for Time Elapsed
COLOR_DOWNLOADS = "\033[92m"  # Green for Videos Downloaded
COLOR_LIBRARY = "\033[93m"  # Yellow for Total Videos in Library
COLOR_STAGE = "\033[95m"  # Purple for Processing Stage
COLOR_VIDEO = "\033[96m"  # Cyan for Video
COLOR_SPEED = "\033[91m"  # Red for Download Speed
COLOR_BANDWIDTH = "\033[90m"  # Gray for Bandwidth Used

# Function to run yt-dlp in the background and collect statistics
def run_yt_dlp(drive_path):
    """Run yt-dlp using embedded commands for the chosen drive."""
    channels_file = os.path.join(drive_path, 'yt-dlp-channels.txt')
    archive_file = os.path.join(drive_path, 'yt-dlp-archive.txt')

    if not os.path.exists(channels_file):
        log_output(f"Channels file not found: {channels_file}")
        print(f"Channels file not found: {channels_file}")
        return

    if not os.path.exists(archive_file):
        log_output(f"Archive file not found: {archive_file}")
        print(f"Archive file not found: {archive_file}")
        return

    print(f"Using channels file: {channels_file}")
    print(f"Using archive file: {archive_file}")

    # Define the absolute output format for the chosen drive
    output_format = os.path.join(drive_path, "%(uploader)s (%(uploader_id)s)/%(upload_date)s - %(title)s.%(ext)s")

    try:
        # Use embedded yt-dlp commands and run it in the background
        command = [
            'yt-dlp',
            '-i',                                # Ignore errors
            '--download-archive', archive_file,   # Archive downloaded videos to prevent re-downloads
            '-o', output_format,                 # Output format, ensure downloading to the correct drive
            '-a', channels_file,                 # Input list of channels/videos to download
            '--format', 'bestvideo[height=1080]+bestaudio/best[height<=1080]/best',  # Best video and audio format
            '--merge-output-format', 'mp4',       # Merge audio and video into MP4 format
            '--embed-thumbnail',                  # Embed thumbnail into video
            '--embed-metadata',                   # Embed metadata into video
            '--cookies-from-browser', 'opera',    # Use cookies from the Opera browser
            '--continue',                         # Continue partially downloaded files
            '--check-formats',                    # Check formats before downloading
            '--ffmpeg-location', ffmpeg_path      # Use ffmpeg from the drive path
        ]

        print(f"Running yt-dlp in the background on {drive_path}...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        return process
    except FileNotFoundError:
        log_output("yt-dlp or ffmpeg not found.")
        print("yt-dlp or ffmpeg not found.")
    except Exception as e:
        log_output(f"yt-dlp execution error: {e}")
        print(f"yt-dlp execution error: {e}")

# Function to track and display statistics
def display_stats(start_time, process, total_videos_initial):
    videos_downloaded = 0
    processing_stage = "Waiting for process..."
    current_video = "No video currently downloading"
    download_speed = "N/A"
    total_videos_in_library = total_videos_initial
    total_bandwidth_start = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent

    download_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%')
    title_pattern = re.compile(r'\[download\] Destination: (.+)')
    speed_pattern = re.compile(r'(\d+\.\d+)\s*M?i?B/s')

    # Display static part of stats initially
    print("\033[H\033[J", end="")  # Clear terminal once at the start
    print(f"{COLOR_TIME}Time elapsed:{COLOR_RESET} 00:00:00")
    print(f"{COLOR_DOWNLOADS}Videos downloaded:{COLOR_RESET} 0")
    print(f"{COLOR_LIBRARY}Total videos in library:{COLOR_RESET} {total_videos_initial}")
    print(f"{COLOR_STAGE}Processing Stage:{COLOR_RESET} Waiting for process...")
    print(f"{COLOR_VIDEO}Video:{COLOR_RESET} No video currently downloading")
    print(f"{COLOR_SPEED}Download speed:{COLOR_RESET} N/A")
    print(f"{COLOR_BANDWIDTH}Bandwidth used:{COLOR_RESET} 0.00 GB\n")

    while process.poll() is None:
        elapsed_seconds = int(time.time() - start_time)
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Calculate bandwidth used in GB
        total_bandwidth_current = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
        bandwidth_used_gb = (total_bandwidth_current - total_bandwidth_start) / (1024 ** 3)  # Convert to GB

        # Position cursor and update each stat line with \033[K to clear the line first
        print(f"\033[H\033[K{COLOR_TIME}Time elapsed:{COLOR_RESET} {elapsed_formatted}")
        print(f"\033[2H\033[K{COLOR_DOWNLOADS}Videos downloaded:{COLOR_RESET} {videos_downloaded}")
        print(f"\033[3H\033[K{COLOR_LIBRARY}Total videos in library:{COLOR_RESET} {total_videos_in_library}")
        print(f"\033[4H\033[K{COLOR_STAGE}Processing Stage:{COLOR_RESET} {processing_stage}")
        print(f"\033[5H\033[K{COLOR_VIDEO}Video:{COLOR_RESET} {current_video}")
        print(f"\033[6H\033[K{COLOR_SPEED}Download speed:{COLOR_RESET} {download_speed}")
        print(f"\033[7H\033[K{COLOR_BANDWIDTH}Bandwidth used:{COLOR_RESET} {bandwidth_used_gb:.2f} GB\n")

        # Read yt-dlp output line-by-line and print it below the stats
        output = process.stdout.readline().strip()

        if output:
            log_output(output)
            print(f"\033[8H\033[K{output}")  # Move cursor to the 8th line and clear it before printing

            # Process video title
            title_match = title_pattern.search(output)
            if title_match:
                current_video = os.path.splitext(os.path.basename(title_match.group(1)))[0]

            # Process stage
            if download_pattern.search(output):
                processing_stage = "Downloading Video"
                speed_match = speed_pattern.search(output)
                download_speed = f"{float(speed_match.group(1))} MB/s" if speed_match else "N/A"
            elif "[Merger]" in output:
                processing_stage = "Merging Formats"
            elif "[Metadata]" in output:
                processing_stage = "Adding Metadata"
            elif "[ThumbnailsConvertor]" in output or "[EmbedThumbnail]" in output:
                processing_stage = "Embedding Thumbnail"
            else:
                processing_stage = "Processing"

            # Update download count when a new video is downloaded
            if "Deleting original file" in output:
                videos_downloaded += 1
                total_videos_in_library += 1

        time.sleep(0.1)

# Run yt-dlp and track stats
yt_dlp_process = run_yt_dlp(drive_path)

if yt_dlp_process:
    start_time = time.time()
    total_videos_initial = count_total_videos(drive_path)

    stats_thread = Thread(target=display_stats, args=(start_time, yt_dlp_process, total_videos_initial), daemon=True)
    stats_thread.start()

    yt_dlp_process.wait()
    print("yt-dlp process finished.")

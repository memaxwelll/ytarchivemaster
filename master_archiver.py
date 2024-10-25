import os
import subprocess
import time
import psutil
from threading import Thread
import re
from datetime import datetime

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_TIME = "\033[94m"  # Blue for Time elapsed
COLOR_DOWNLOADS = "\033[92m"  # Green for Videos downloaded
COLOR_LIBRARY = "\033[93m"  # Yellow for Total videos in library
COLOR_STAGE = "\033[95m"  # Purple for Processing Stage
COLOR_VIDEO = "\033[96m"  # Cyan for Current Video
COLOR_SPEED = "\033[91m"  # Red for Download speed
COLOR_BANDWIDTH = "\033[90m"  # Gray for Bandwidth used
COLOR_DISK = "\033[93m"  # Yellow for Disk info

# Define the directories for each drive option
directories_map = {
    '1': 'D:\\YT',
    '2': 'E:\\YT',
    '3': 'F:\\YT',
    '4': 'ALL'
}

# Function to prompt the user to select the drive
def get_drive_selection():
    print("Select the drive to update:")
    print("1 = D:\\YT")
    print("2 = E:\\YT")
    print("3 = F:\\YT")
    print("4 = ALL drives")

    selection = input("Enter your choice (1, 2, 3, 4): ").strip()

    if selection not in directories_map:
        print("Invalid input. Please enter 1, 2, 3, or 4.")
        return get_drive_selection()  # Ask again if the input is invalid

    return selection

# Function to count total videos on the drive
def count_total_videos(drive_path):
    """Count the total number of videos in the library based on the downloaded video structure."""
    video_count = 0
    for root, dirs, files in os.walk(drive_path):
        for file in files:
            if file.endswith(".mp4"):  # Assuming videos are in MP4 format
                video_count += 1
    return video_count

# Function to get disk usage information
def get_disk_usage(drive_path):
    """Return disk usage info: total capacity in TB, available space in GB, and remaining percentage."""
    usage = psutil.disk_usage(drive_path)
    total_capacity_tb = usage.total / (1024 ** 4)  # Convert to TB
    available_gb = usage.free / (1024 ** 3)  # Convert to GB
    remaining_percent = 100 - usage.percent  # Calculate remaining percentage
    return total_capacity_tb, available_gb, remaining_percent

# Function to run yt-dlp on the selected drive
def run_yt_dlp_on_drive(drive_path):
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
            '--ffmpeg-location', os.path.join(drive_path, 'ffmpeg') # Use ffmpeg from the drive path
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

# Logging function for yt-dlp output
def log_output(line):
    """Log yt-dlp output to yt-dlp.log file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("yt-dlp.log", 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {line}\n")

# Stats display function
def display_stats(start_time, process, total_videos_initial, drive_path):
    videos_downloaded = 0
    processing_stage = "Waiting for process..."
    current_video = "No video currently downloading"
    download_speed = "N/A"
    total_videos_in_library = total_videos_initial
    total_bandwidth_start = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent

    # Initial disk usage information
    total_capacity_tb, available_gb, remaining_percent = get_disk_usage(drive_path)

    download_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%')
    title_pattern = re.compile(r'\[download\] Destination: (.+)')
    speed_pattern = re.compile(r'(\d+\.\d+)\s*M?i?B/s')
    merger_pattern = re.compile(r'\[Merger\] Merging formats into')  # Detect the merger process

    # Reserve the first 8 lines for stats display
    while process.poll() is None:
        elapsed_seconds = int(time.time() - start_time)
        elapsed_formatted = f"{elapsed_seconds // 3600:02}:{(elapsed_seconds % 3600) // 60:02}:{elapsed_seconds % 60:02}"

        # Calculate bandwidth used in GB
        total_bandwidth_current = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
        bandwidth_used_gb = (total_bandwidth_current - total_bandwidth_start) / (1024 ** 3)  # Convert to GB

        # Move cursor and clear each line before updating the stat values
        print(f"\033[H\033[K{COLOR_TIME}Time elapsed: {COLOR_RESET}{elapsed_formatted}")
        print(f"\033[2H\033[K{COLOR_DOWNLOADS}Videos downloaded: {COLOR_RESET}{videos_downloaded}")
        print(f"\033[3H\033[K{COLOR_LIBRARY}Total videos in library: {COLOR_RESET}{total_videos_in_library}")
        print(f"\033[4H\033[K{COLOR_STAGE}Processing Stage: {COLOR_RESET}{processing_stage}")
        print(f"\033[5H\033[K{COLOR_VIDEO}Video: {COLOR_RESET}{current_video}")
        print(f"\033[6H\033[K{COLOR_SPEED}Download speed: {COLOR_RESET}{download_speed}")
        print(f"\033[7H\033[K{COLOR_BANDWIDTH}Bandwidth used: {COLOR_RESET}{bandwidth_used_gb:.2f} GB")
        print(f"\033[8H\033[K{COLOR_DISK}Disk {drive_path}: Capacity {total_capacity_tb:.2f} TB | Available {available_gb:.2f} GB | Remaining {remaining_percent:.2f}%{COLOR_RESET}\n")

        # Process yt-dlp output
        output = process.stdout.readline().strip()
        if output:
            log_output(output)

            # Display yt-dlp output in one line below stats (line 9), limit the width to prevent overflow
            terminal_width = os.get_terminal_size().columns  # Get the terminal width
            max_output_len = terminal_width - 10  # Leave some margin for safety
            if len(output) > max_output_len:
                output = output[:max_output_len - 3] + '...'  # Truncate the output and add "..." if it's too long

            print(f"\033[9H\033[K{output}")  # Move cursor to line 9 and clear the line for yt-dlp output

            # Track the download stage
            title_match = title_pattern.search(output)
            if title_match:
                current_video = os.path.splitext(os.path.basename(title_match.group(1)))[0]

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

            # Detect video completion based on "Merging formats" message in the merger step
            if merger_pattern.search(output):
                videos_downloaded += 1  # Only count as a completed download after merging
                total_videos_in_library += 1

                # Update disk stats after each video is fully processed
                total_capacity_tb, available_gb, remaining_percent = get_disk_usage(drive_path)

        time.sleep(0.1)

# Run yt-dlp on each drive sequentially if "ALL" is selected
def run_yt_dlp_on_selected_drives(selection):
    if selection == '4':  # Run on all drives sequentially
        for drive in ['D:\\YT', 'E:\\YT', 'F:\\YT']:
            process = run_yt_dlp_on_drive(drive)
            if process:
                start_time = time.time()
                total_videos_initial = count_total_videos(drive)
                stats_thread = Thread(target=display_stats, args=(start_time, process, total_videos_initial, drive), daemon=True)
                stats_thread.start()
                process.wait()
                print(f"yt-dlp process finished on {drive}.")
    else:
        drive = directories_map[selection]
        process = run_yt_dlp_on_drive(drive)
        if process:
            # Clear terminal after the user selects the drive
            print("\033[H\033[J")  # Clear the entire screen
            start_time = time.time()
            total_videos_initial = count_total_videos(drive)
            stats_thread = Thread(target=display_stats, args=(start_time, process, total_videos_initial, drive), daemon=True)
            stats_thread.start()
            process.wait()
            print(f"yt-dlp process finished on {drive}.")

# Main execution
selection = get_drive_selection()
run_yt_dlp_on_selected_drives(selection)

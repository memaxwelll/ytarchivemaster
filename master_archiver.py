import os
import json
import subprocess
import time
import psutil
from threading import Thread
import re
import requests  # New import for handling HTTP requests

# ANSI color codes for display
COLOR_RESET = "\033[0m"
COLOR_TIME = "\033[94m"  # Blue for Time elapsed
COLOR_DOWNLOADS = "\033[92m"  # Green for Videos downloaded
COLOR_LIBRARY = "\033[93m"  # Yellow for Total videos in library
COLOR_STAGE = "\033[95m"  # Purple for Processing Stage
COLOR_VIDEO = "\033[96m"  # Cyan for Current Video
COLOR_SPEED = "\033[91m"  # Red for Download speed
COLOR_BANDWIDTH = "\033[90m"  # Gray for Bandwidth used
COLOR_DISK = "\033[93m"  # Yellow for Disk info

# Configuration file
CONFIG_FILE = 'config.json'
SCRIPT_URL = 'https://github.com/memaxwelll/ytarchivemaster/blob/main/master_archiver.py'

# Load or create default configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        '1': 'D:\\YT',
        '2': 'E:\\YT',
        '3': 'F:\\YT'
    }

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Check for updates and prompt user
def check_for_updates():
    try:
        response = requests.get(SCRIPT_URL)
        if response.status_code == 200:
            latest_script_content = response.text
            current_script_path = os.path.abspath(__file__)
            
            # Compare with the current script
            with open(current_script_path, 'r') as current_script:
                current_script_content = current_script.read()
            
            if latest_script_content != current_script_content:
                user_input = input("An update is available. Would you like to download the latest version? (Y/N): ").strip().lower()
                if user_input == 'y':
                    print("Downloading the latest version...")
                    with open(current_script_path, 'w') as current_script:
                        current_script.write(latest_script_content)
                    print("Update completed. Please restart the script.")
                    exit(0)  # Exit after updating
                else:
                    print("You chose not to update. Continuing with the current version.")
            else:
                print("You are using the latest version of the script.")
    except Exception as e:
        print(f"Error checking for updates: {e}")

# Modify paths interactively
def modify_paths(config):
    while True:
        print("\nCurrent paths:")
        for key, path in config.items():
            print(f"{key} = {path}")

        action = input("\nChoose action - (A)dd, (M)odify, (R)emove, (B)ack: ").strip().lower()
        if action == 'a':
            new_key = str(max(map(int, config.keys())) + 1)
            new_path = input(f"Enter path for {new_key}: ").strip()
            config[new_key] = new_path
            save_config(config)  # Save changes immediately
        elif action == 'm':
            key_to_modify = input("Enter the number of the path to modify: ").strip()
            if key_to_modify in config:
                new_path = input(f"Enter new path for {key_to_modify}: ").strip()
                config[key_to_modify] = new_path
                save_config(config)  # Save changes immediately
            else:
                print("Invalid key.")
        elif action == 'r':
            key_to_remove = input("Enter the number of the path to remove: ").strip()
            if key_to_remove in config:
                del config[key_to_remove]
                save_config(config)  # Save changes immediately
            else:
                print("Invalid key.")
        elif action == 'b':
            return config
        else:
            print("Invalid option. Please choose A, M, R, or B to go back.")

# Get user-selected drive
def get_drive_selection(config):
    while True:
        print("\nSelect the drive to update:")
        for key, path in config.items():
            print(f"{key} = {path}")
        print(f"{len(config) + 1} = ALL drives")

        selection = input("Enter your choice or type (C)onfigure to change paths: ").strip()
        if selection == 'c':
            config = modify_paths(config)
        elif selection in config or selection == str(len(config) + 1):
            return selection, config
        else:
            print("Invalid input. Please enter a valid option.")

# Count total videos on the drive
def count_total_videos(drive_path):
    return sum(1 for _, _, files in os.walk(drive_path) for file in files if file.endswith(".mp4"))

# Get disk usage information
def get_disk_usage(drive_path):
    usage = psutil.disk_usage(drive_path)
    total_capacity_tb = usage.total / (1024 ** 4)
    available_gb = usage.free / (1024 ** 3)
    remaining_percent = 100 - usage.percent
    return total_capacity_tb, available_gb, remaining_percent

# Display statistics during download
def display_stats(start_time, process, total_videos_initial, drive_path):
    if process is None:
        print("The yt-dlp process could not be started.")
        return
    
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

    while process.poll() is None:
        elapsed_seconds = int(time.time() - start_time)
        elapsed_formatted = f"{elapsed_seconds // 3600:02}:{(elapsed_seconds % 3600) // 60:02}:{elapsed_seconds % 60:02}"

        # Calculate bandwidth used in GB
        total_bandwidth_current = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
        bandwidth_used_gb = (total_bandwidth_current - total_bandwidth_start) / (1024 ** 3)  # Convert to GB

        # Update stats display
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
            output = output.decode('utf-8', errors='replace').strip()

            # Display yt-dlp output
            terminal_width = os.get_terminal_size().columns
            max_output_len = terminal_width - 10
            if len(output) > max_output_len:
                output = output[:max_output_len - 3] + '...'

            print(f"\033[9H\033[K{output}")  # Display yt-dlp output

            # Track download stage
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

            # Check for video completion
            if merger_pattern.search(output):
                videos_downloaded += 1
                total_videos_in_library += 1

                # Update disk stats after each video is fully processed
                total_capacity_tb, available_gb, remaining_percent = get_disk_usage(drive_path)

        time.sleep(0.1)

# Run yt-dlp on the selected drive
def run_yt_dlp_on_drive(drive_path):
    channels_file = os.path.join(drive_path, 'yt-dlp-channels.txt')
    archive_file = os.path.join(drive_path, 'yt-dlp-archive.txt')
    output_format = os.path.join(drive_path, "%(uploader)s (%(uploader_id)s)/%(upload_date)s - %(title)s.%(ext)s")

    try:
        command = [
            'yt-dlp',
            '-i',                                # Ignore errors
            '--download-archive', archive_file,   # Archive downloaded videos
            '-o', output_format,                 # Output format
            '-a', channels_file,                 # Input list of channels/videos to download
            '--format', 'bestvideo[height=1080]+bestaudio/best[height<=1080]/best',
            '--merge-output-format', 'mp4',       # Merge audio and video
            '--embed-thumbnail',                  # Embed thumbnail into video
            '--embed-metadata',                   # Embed metadata into video
            '--cookies-from-browser', 'opera',    # Use cookies from the Opera browser
            '--continue',                         # Continue partially downloaded files
            '--check-formats',                    # Check formats before downloading
            '--ffmpeg-location', os.path.join(drive_path, 'ffmpeg')
        ]

        print(f"Running yt-dlp in the background on {drive_path}...")
        process = subprocess.Popen(command, cwd=drive_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return process
    except FileNotFoundError:
        print("yt-dlp or ffmpeg not found.")
        return None

# Run yt-dlp on each selected drive
def run_yt_dlp_on_selected_drives(selection, config):
    if selection == str(len(config) + 1):  # "ALL" option selected
        for drive in config.values():
            process = run_yt_dlp_on_drive(drive)
            if process:
                start_time = time.time()
                total_videos_initial = count_total_videos(drive)
                stats_thread = Thread(target=display_stats, args=(start_time, process, total_videos_initial, drive), daemon=True)
                stats_thread.start()
                process.wait()  # Wait for yt-dlp process to finish
                print(f"yt-dlp process finished on {drive}.")
    else:
        drive = config[selection]
        process = run_yt_dlp_on_drive(drive)
        if process:
            print("\033[H\033[J")  # Clear the entire screen
            start_time = time.time()
            total_videos_initial = count_total_videos(drive)
            stats_thread = Thread(target=display_stats, args=(start_time, process, total_videos_initial, drive), daemon=True)
            stats_thread.start()
            process.wait()  # Wait for yt-dlp process to finish
            print(f"yt-dlp process finished on {drive}.")

# Main execution
check_for_updates()  # Check for updates before proceeding
config = load_config()  # Load paths from config file or use defaults
selection, config = get_drive_selection(config)

# Clear the screen after user selection
print("\033[H\033[J")  # Clear the entire screen
run_yt_dlp_on_selected_drives(selection, config)  # Run yt-dlp on selected drives

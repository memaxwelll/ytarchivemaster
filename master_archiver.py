import os
import json
import subprocess
import time
import psutil
from threading import Thread, Lock
import re

# ANSI color codes for display
COLOR_RESET = "\033[0m"
COLOR_TIME = "\033[94m"
COLOR_DOWNLOADS = "\033[92m"
COLOR_LIBRARY = "\033[93m"
COLOR_STAGE = "\033[95m"
COLOR_VIDEO = "\033[96m"
COLOR_SPEED = "\033[91m"
COLOR_BANDWIDTH = "\033[90m"
COLOR_DISK = "\033[93m"

# Configuration file and log file
CONFIG_FILE = 'config.json'
LOG_FILE = 'yt-dlp.log'

# Shared stats dictionary and lock for thread-safe updates
stats = {
    "videos_downloaded": 0,
    "total_videos_in_library": 0,
    "processing_stage": "Waiting for process...",
    "current_video": "No video currently downloading",
    "download_speed": "N/A",
    "bandwidth_used_gb": 0,
    "total_capacity_tb": 0,
    "available_gb": 0,
    "remaining_percent": 0,
    "time_elapsed": 0
}
lock = Lock()

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
            save_config(config)
        elif action == 'm':
            key_to_modify = input("Enter the number of the path to modify: ").strip()
            if key_to_modify in config:
                new_path = input(f"Enter new path for {key_to_modify}: ").strip()
                config[key_to_modify] = new_path
                save_config(config)
            else:
                print("Invalid key.")
        elif action == 'r':
            key_to_remove = input("Enter the number of the path to remove: ").strip()
            if key_to_remove in config:
                del config[key_to_remove]
                save_config(config)
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
        if selection.lower() == 'c':
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

# Log yt-dlp output with timestamp
def log_output(output):
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp} - {output}\n")

# Function to start yt-dlp process on a specific drive
def start_yt_dlp_process(drive_path):
    command = [
        'yt-dlp',
        '-i',
        '--download-archive', os.path.join(drive_path, 'yt-dlp-archive.txt'),
        '-o', os.path.join(drive_path, '%(uploader)s (%(uploader_id)s)/%(upload_date)s - %(title)s.%(ext)s'),
        '-a', os.path.join(drive_path, 'yt-dlp-channels.txt'),
        '--format', 'bestvideo[height=1080]+bestaudio/best[height<=1080]/best',
        '--merge-output-format', 'mp4',
        '--embed-thumbnail',
        '--embed-metadata',
        '--cookies-from-browser', 'opera',
        '--continue',
        '--check-formats'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process

# Function to update elapsed time independently
def update_time_elapsed():
    while True:
        with lock:
            stats["time_elapsed"] += 1
        time.sleep(1)

# Function to display stats
def display_stats(drive_path):
    while True:
        elapsed_formatted = f"{stats['time_elapsed'] // 3600:02}:{(stats['time_elapsed'] % 3600) // 60:02}:{stats['time_elapsed'] % 60:02}"
        
        with lock:
            print(f"\033[H\033[K{COLOR_TIME}Time elapsed: {COLOR_RESET}{elapsed_formatted}")
            print(f"\033[2H\033[K{COLOR_DOWNLOADS}Videos downloaded: {COLOR_RESET}{stats['videos_downloaded']}")
            print(f"\033[3H\033[K{COLOR_LIBRARY}Total videos in library: {COLOR_RESET}{stats['total_videos_in_library']}")
            print(f"\033[4H\033[K{COLOR_STAGE}Processing Stage: {COLOR_RESET}{stats['processing_stage']}")
            print(f"\033[5H\033[K{COLOR_VIDEO}Video: {COLOR_RESET}{stats['current_video']}")
            print(f"\033[6H\033[K{COLOR_SPEED}Download speed: {COLOR_RESET}{stats['download_speed']}")
            print(f"\033[7H\033[K{COLOR_BANDWIDTH}Bandwidth used: {COLOR_RESET}{stats['bandwidth_used_gb']:.2f} GB")
            print(f"\033[8H\033[K{COLOR_DISK}Disk {drive_path}: Capacity {stats['total_capacity_tb']:.2f} TB | Available {stats['available_gb']:.2f} GB | Remaining {stats['remaining_percent']:.2f}%{COLOR_RESET}\n")
        
        time.sleep(1)

# Parse and update stats from yt-dlp output
def parse_yt_dlp_output(process, drive_path):
    total_bandwidth_start = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
    download_pattern = re.compile(r'\[download\]\s+(\d+\.\d+)%')
    title_pattern = re.compile(r'\[download\] Destination: (.+)')
    speed_pattern = re.compile(r'(\d+\.\d+)\s*M?i?B/s')
    merger_pattern = re.compile(r'\[Merger\] Merging formats into')

    while process.poll() is None:
        output = process.stdout.readline()
        if output:
            output_decoded = output.decode('utf-8', errors='replace').strip()  # Decode here
            log_output(output_decoded)  # Log output

            # Truncate yt-dlp output if it's too long for one line
            terminal_width = os.get_terminal_size().columns
            max_output_length = terminal_width - 10  # Leave a margin for aesthetics
            if len(output_decoded) > max_output_length:
                output_decoded = output_decoded[:max_output_length - 3] + "..."  # Truncate and add ellipsis

            # Clear and update the same line for yt-dlp output
            print(f"\033[9H\033[K{output_decoded}", end='\r')  # Move to line 9, clear line, print output

            with lock:
                title_match = title_pattern.search(output_decoded)
                if title_match:
                    stats["current_video"] = os.path.splitext(os.path.basename(title_match.group(1)))[0]

                # Download progress and speed
                if download_pattern.search(output_decoded):
                    stats["processing_stage"] = "Downloading Video"
                    speed_match = speed_pattern.search(output_decoded)
                    stats["download_speed"] = f"{float(speed_match.group(1))} MB/s" if speed_match else "N/A"
                elif "[Merger]" in output_decoded:
                    stats["processing_stage"] = "Merging Formats"
                elif "[Metadata]" in output_decoded:
                    stats["processing_stage"] = "Adding Metadata"
                elif "[ThumbnailsConvertor]" in output_decoded or "[EmbedThumbnail]" in output_decoded:
                    stats["processing_stage"] = "Embedding Thumbnail"
                else:
                    stats["processing_stage"] = "Processing"

                # Check for video completion
                if merger_pattern.search(output_decoded):
                    stats["videos_downloaded"] += 1
                    stats["total_videos_in_library"] += 1

                # Update bandwidth
                total_bandwidth_current = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
                stats["bandwidth_used_gb"] = (total_bandwidth_current - total_bandwidth_start) / (1024 ** 3)

        time.sleep(0.1)

# Start threads for drive processing
def start_threads_for_drive(process, drive_path):
    stats["total_videos_in_library"] = count_total_videos(drive_path)
    disk_capacity, disk_available, disk_remaining = get_disk_usage(drive_path)
    with lock:
        stats["total_capacity_tb"] = disk_capacity
        stats["available_gb"] = disk_available
        stats["remaining_percent"] = disk_remaining

    # Start time and stats display threads
    time_thread = Thread(target=update_time_elapsed, daemon=True)
    time_thread.start()

    stats_thread = Thread(target=display_stats, args=(drive_path,), daemon=True)
    stats_thread.start()

    yt_dlp_thread = Thread(target=parse_yt_dlp_output, args=(process, drive_path), daemon=True)
    yt_dlp_thread.start()

    yt_dlp_thread.join()

# Run yt-dlp on selected drives
def run_yt_dlp_on_selected_drives(selection, config):
    if selection == str(len(config) + 1):  # ALL option
        for drive_path in config.values():
            process = start_yt_dlp_process(drive_path)
            start_threads_for_drive(process, drive_path)
    else:
        drive_path = config[selection]
        process = start_yt_dlp_process(drive_path)
        start_threads_for_drive(process, drive_path)

# Main execution
config = load_config()
selection, config = get_drive_selection(config)

print("\033[H\033[J")  # Clear the screen
run_yt_dlp_on_selected_drives(selection, config)

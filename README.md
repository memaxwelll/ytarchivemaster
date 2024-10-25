# YouTube Video Archiver

This script automates the downloading, processing, and archiving of YouTube videos from specified channels onto a user-defined drive. It provides real-time statistics on download progress, bandwidth usage, and storage information while keeping track of archived videos to prevent duplicate downloads.

## Features

- **User-Defined Drive Selection**: Choose the drive where videos should be stored and processed.
- **Real-Time Download Statistics**:
  - Time elapsed since the script started
  - Number of videos downloaded
  - Total videos in the library
  - Current processing stage (e.g., downloading, merging, embedding metadata)
  - Current video being processed
  - Download speed and bandwidth usage
- **Persistent Logging**: Outputs are logged to a `yt-dlp.log` file with timestamps for future reference.
- **Archive Management**: Uses `yt-dlp-archive.txt` to avoid re-downloading videos by tracking previously downloaded videos.

## Screenshot
![alt text](https://i.ibb.co/GWNyR9B/2024-10-25-10-24-36-Desktop-and-3-more-tabs-File-Explorer.png)
![alt text](https://i.ibb.co/MGhpmjt/2024-10-25-10-34-57-Img-BB-Bild-hochladen-Kostenloses-Bild-Hosting-Opera.png)

## Requirements

### Python and Packages
- **Python Version**: Python 3.8 or higher is required.
- **Python Packages**:
  - Install the necessary dependencies with `pip install -r requirements.txt`.
  - Required packages:
    - `psutil`: For real-time system and network statistics.
    
### External Tools
- **ffmpeg**: Required by `yt-dlp` for processing video and audio files. Ensure `ffmpeg` is available on each selected drive.
- **yt-dlp**: For downloading videos and managing YouTube content. It should be installed and added to your system’s PATH.

## Setup for Windows
1. Clone this repository and navigate to the project directory:
```bash
git clone https://github.com/yourusername/youtube-archiver.git
cd youtube-archiver
```
2. Install the Python dependencies:
```bash
pip install -r requirements.txt
```
3. Download ffmpeg (Full Release) and yt-dlp (latest version). Make sure yt-dlp is added to system's PATH and ffmpeg is available on the drive in subfolger "ffmpeg".
4. If neccesarry change the drives and paths in the script. You can also change the yt-dlp flags according to your needs.
5. Start the script and select the drive where you want to save the downloaded videos. The script will start downloading and processing videos based on the settings in your yt-dlp-channels.txt and yt-dlp-archive.txt files.

## Usage

### Notes
- Place yt-dlp-channels.txt (for channels and playlists) and yt-dlp-archive.txt (for tracking downloaded videos) on the selected drive.
- Logging: The script logs download progress and errors to yt-dlp.log in the current working directory.
- Configuration Files: The yt-dlp settings are configured directly in the script, but yt-dlp-channels.txt and yt-dlp-archive.txt must be present on each drive.

### Example File Structure

Ensure your file structure matches the following on each selected drive:
```
D:\
└── YT\
    ├── yt-dlp-archive.txt      # Track downloaded videos to avoid duplicates
    ├── yt-dlp-channels.txt     # List of YouTube channels or playlists to download
    └── ffmpeg                  # ffmpeg binary for processing video and audio
```

### Troubleshooting

- Permissions: Ensure you have read/write permissions for the selected drive.
- ffmpeg and yt-dlp Accessibility: Ensure both ffmpeg and yt-dlp are accessible on each drive.
- Logs: Check yt-dlp.log for error details if any downloads fail.

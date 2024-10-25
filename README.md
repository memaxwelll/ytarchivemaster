# YouTube Video Archiver

This script automates the downloading, processing, and archiving of YouTube videos from specified channels onto a user-defined drive. It provides real-time statistics on download progress, bandwidth usage, and storage information while keeping track of archived videos to prevent duplicate downloads.

## Features

- **User-Defined Drive Selection**: Choose the drive (D, E, or F) where videos should be stored and processed.
- **Real-Time Download Statistics**:
  - Time elapsed since the script started
  - Number of videos downloaded
  - Total videos in the library
  - Current processing stage (e.g., downloading, merging, embedding metadata)
  - Current video being processed
  - Download speed and bandwidth usage
- **Persistent Logging**: Outputs are logged to a `yt-dlp.log` file with timestamps for future reference.
- **Archive Management**: Uses `yt-dlp-archive.txt` to avoid re-downloading videos by tracking previously downloaded videos.

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

### Example File Structure

Ensure your file structure matches the following on each selected drive:

D:\
└── YT\
    ├── yt-dlp-archive.txt      # Track downloaded videos to avoid duplicates
    ├── yt-dlp-channels.txt     # List of YouTube channels or playlists to download
    └── ffmpeg                  # ffmpeg binary for processing video and audio

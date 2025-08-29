# Video Duration Tool

A simple CLI tool to calculate durations of MP4 files in a folder.

## Installation
pip install .

## Usage
video-duration /path/to/your/folder

## Requirements
- Python 3.6+
- ffmpeg (required for ffprobe, which extracts video metadata). This must be installed separately on your system and available in your PATH.

### Installing ffmpeg
- **macOS**: Use Homebrew: `brew install ffmpeg`. If you don't have Homebrew, install it from https://brew.sh/.

- **Windows**:
Download the latest build from https://ffmpeg.org/download.html (choose a "Windows builds from gyan.dev" or similar). Extract it, add the `bin` folder to your system PATH (search online for "add to PATH on Windows"), and restart your terminal.

- **Linux (Ubuntu/Debian)**: 
`sudo apt update && sudo apt install ffmpeg`.

- **Linux (Fedora)**: 
`sudo dnf install ffmpeg`.

- **Other platforms**: 
Visit https://ffmpeg.org/download.html for binaries or package manager instructions.

If ffmpeg is not installed, the tool will print an error with these instructions.
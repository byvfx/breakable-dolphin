# Breakable Dolphin - Testing Area

This repository is a small testing area for various video downloading scripts.

## Overview

- **ytdlp_squarespace.py**: A specialized downloader for Squarespace-hosted videos. Handles authentication, token refresh, and HLS stream downloads. Requires proper environment variables setup (see Environment Setup section).
- **ytdlp_pysimplegui.py**: A GUI application using PySimpleGUI and yt-dlp to manage a download queue.
- **ytdlp_class_instance.py**: A script that reads video URLs from a file and downloads videos using yt-dlp.
- **ytdlp_txt_queue.py**: A variant that iterates through a list of video URLs, downloading each in sequence.
- **ytdlp_queue.py**: A simple script that downloads videos sequentially from a predefined list.
- **ytdlp_parallel.py**: A script that uses concurrent threads to download videos concurrently.

## Installation

### Using pip

To install the required packages:
```bash
pip install -r requirements.txt
```

### Using conda

Since the environment was created with conda, you can recreate it with:
```bash
conda create --name <env> --file requirements.txt
```

## Environment Setup for Squarespace Downloader

The Squarespace downloader requires specific environment variables to be set in a `.env` file. For security reasons, these are not included in the repository.

### Creating your .env file

Create a file named `.env` in the `src` directory with the following structure:
```
BASE_URL=https://www.yourdomain.com
COOKIES_STR=your_cookie_string_here
CSRF_TOKEN=your_csrf_token_here
```

### How to obtain the required values

1. **Cookie String (COOKIES_STR)**:
   - Open your browser's Developer Tools (F12)
   - Go to the Network tab
   - Play any video on your Squarespace site
   - Click on any request
   - In the Headers tab, find "Cookie" under Request Headers
   - Copy the entire cookie string

2. **CSRF Token (CSRF_TOKEN)**:
   - In the same Network tab view
   - Look for "x-csrf-token" in the request headers
   - Copy the token value

3. **Base URL (BASE_URL)**:
   - This is your Squarespace site's main domain
   - Example: https://www.yourdomain.com

### Troubleshooting Network Inspection

If you're not seeing video-related requests:
1. Clear the Network tab (🚫 icon)
2. Enable "Preserve log"
3. Play the video
4. Look for requests ending in `.m3u8`

### Security Note

- Never commit your `.env` file to version control
- Keep your authentication tokens secure
- Refresh your cookies if downloads stop working
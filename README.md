# Breakable Dolphin - Testing Area

This repository is a small testing area for various video downloading scripts.

## Overview

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
import PySimpleGUI as sg
import yt_dlp
import threading
import queue
import re

sg.theme('DarkGrey9')

download_queue = queue.Queue()

# Function to download a video
def download_video(url, window):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'best',
        'noplaylist': True,
        'quiet': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            window.write_event_value('-UPDATE-', f"Starting download: {url}")
            ydl.download([url])
            window.write_event_value('-UPDATE-', f"Finished download: {url}")
        except Exception as e:
            window.write_event_value('-UPDATE-', f"Error downloading {url}: {e}")

# Function to manage the queue
def queue_manager(window):
    while True:
        url = download_queue.get()
        if url is None:
            break  
        download_video(url, window)

# New helper function to validate URLs
def is_valid_url(url):
    pattern = re.compile(r'^(http|https)://')
    return pattern.match(url) is not None

# Layout
layout = [
    [sg.Text("Enter Video URL:")],
    [sg.InputText(key="-URL-", size=(50, 1)), sg.Button("Add to Queue")],
    [sg.Listbox(values=[], size=(50, 10), key="-QUEUE-", enable_events=True)],
    [sg.Button("Start Downloads"), sg.Button("Exit")],
    [sg.Multiline(size=(50, 10), key="-LOG-", disabled=True, autoscroll=True)]
]

# Create the window
window = sg.Window("Video Download Manager", layout)

# Download thread might add thread management later
download_thread = threading.Thread(target=queue_manager, args=(window,), daemon=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    elif event == "Add to Queue":
        url = values["-URL-"].strip()
        if url:
            if not is_valid_url(url):
                window["-LOG-"].print(f"Error: Invalid URL format for input: {url}")
            else:
                download_queue.put(url)
                window["-QUEUE-"].update(values=list(download_queue.queue))
                window["-LOG-"].print(f"Added to queue: {url}")

    elif event == "Start Downloads":
        if not download_thread.is_alive():
            download_thread = threading.Thread(target=queue_manager, args=(window,), daemon=True)
            download_thread.start()
            window["-LOG-"].print("Starting downloads...")

    elif event == "-UPDATE-":
        window["-LOG-"].print(values[event])

window.close()

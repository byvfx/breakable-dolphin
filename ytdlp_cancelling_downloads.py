import yt_dlp
import threading
import time

class Downloader:
    def __init__(self):
        self.stop_event = threading.Event()

    def download(self, url):
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            while not self.stop_event.is_set():
                try:
                    ydl.download([url])
                    break  # Exit loop if download completes
                except Exception as e:
                    print(f"Error: {e}")
                    break

    def stop(self):
        self.stop_event.set()

# Usage
downloader = Downloader()
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Start download in a thread
download_thread = threading.Thread(target=downloader.download, args=(url,))
download_thread.start()

# Let it run for a bit
time.sleep(5)

# Cancel the download
print("Cancelling download...")
downloader.stop()
download_thread.join()
print("Download cancelled or completed.")
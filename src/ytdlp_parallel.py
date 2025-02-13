import yt_dlp
import concurrent.futures

video_urls = [
    
    "https://www.youtube.com/watch?v=5Va8k0KQfZU",
    "https://www.youtube.com/watch?v=LvTEJdtxVSA",

]

def download_video(url):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'best',
        'noplaylist': True,
        'quiet': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Starting download: {url}")
            ydl.download([url])
            print(f"Finished download: {url}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

max_threads = 3  
with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
    executor.map(download_video, video_urls)

print("All downloads completed mane")

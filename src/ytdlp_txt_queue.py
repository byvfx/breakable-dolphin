import yt_dlp

video_list = "src/video_list.txt"

# this reads the video urls from a file just copy and paste this in the parallel script, this will overwrite the video_urls list
with open(video_list) as f:
    video_urls = [line.strip() for line in f if line.strip()]



ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
    'format': 'best',
    'noplaylist': True,
    'quiet': False,
}


with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in video_urls:
        print(f"Downloading: {url}")
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Error downloading {url}: {e}")

print("All downloads completed mane")

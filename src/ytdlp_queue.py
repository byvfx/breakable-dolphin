import yt_dlp

video_urls = [
    
    "https://www.youtube.com/watch?v=5Va8k0KQfZU",
    "https://www.youtube.com/watch?v=LvTEJdtxVSA",

]


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

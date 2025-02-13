from yt_dlp import YoutubeDL

video_list = "src/video_list.txt"

with open(video_list) as f:
    video_urls = [line.strip() for line in f if line.strip()]
    
ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
    'format': 'best',
    'noplaylist': True,
    'quiet': False,
}


ydl = YoutubeDL(ydl_opts)

for url in video_urls:
    ydl.download([url]) 

print("All downloads complete mane")
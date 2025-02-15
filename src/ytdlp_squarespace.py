from yt_dlp import YoutubeDL
import m3u8
import requests
import re
from urllib.parse import urlparse, parse_qs

def download_squarespace_videos(video_list_path, auth_token, cookies_str):
    # Parse cookies string into a dictionary
    cookies = {}
    for cookie in cookies_str.split('; '):
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookies[name] = value

    # Read URLs from the text file
    with open(video_list_path) as f:
        video_urls = [line.strip() for line in f if line.strip()]

    # Headers for segment requests
    segment_headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.breakyourcrayons.com',
        'referer': 'https://www.breakyourcrayons.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
    }

    # Headers for m3u8 requests
    m3u8_headers = {
        **segment_headers,
        'Authorization': auth_token,
        'Cookie': cookies_str
    }

    def get_signed_url(url, session):
        """Get signed URL for video segments"""
        try:
            response = session.get(url, headers=m3u8_headers)
            if response.status_code == 200:
                # Parse the m3u8 content
                m3u8_obj = m3u8.loads(response.text)
                # Find the highest quality playlist
                if m3u8_obj.playlists:
                    max_bandwidth = max(p.stream_info.bandwidth for p in m3u8_obj.playlists)
                    best_playlist = next(p for p in m3u8_obj.playlists if p.stream_info.bandwidth == max_bandwidth)
                    
                    # Get the variant playlist URL
                    variant_url = best_playlist.uri
                    if not variant_url.startswith('http'):
                        # Make the URL absolute if it's relative
                        base_url = '/'.join(url.split('/')[:-1])
                        variant_url = f"{base_url}/{variant_url}"
                    
                    print(f"Found variant playlist: {variant_url}")
                    return variant_url
            return None
        except Exception as e:
            print(f"Error getting signed URL: {str(e)}")
            return None

    # Process each URL
    for url in video_urls:
        try:
            print(f"\nProcessing URL: {url}")
            
            # Create a session for consistent cookies
            session = requests.Session()
            session.headers.update(segment_headers)
            
            # Get the signed URL for the highest quality variant
            signed_url = get_signed_url(url, session)
            if not signed_url:
                print("Could not get signed URL")
                continue

            # Configure yt-dlp options for the signed URL
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloaded_video.mp4',
                'quiet': False,
                'verbose': True,
                'prefer_ffmpeg': True,
                'external_downloader': 'ffmpeg',
                'external_downloader_args': {
                    'ffmpeg_i': [
                        '-headers',
                        '\n'.join([
                            'Accept: */*',
                            'Accept-Language: en-US,en;q=0.9',
                            'Origin: https://www.breakyourcrayons.com',
                            'Referer: https://www.breakyourcrayons.com/',
                            f'User-Agent: {segment_headers["user-agent"]}'
                        ])
                    ]
                },
                'http_headers': segment_headers,
                'hls_prefer_ffmpeg': True,
                'hls_use_mpegts': True
            }

            # Download using yt-dlp
            with YoutubeDL(ydl_opts) as ydl:
                print(f"Attempting to download from signed URL: {signed_url}")
                ydl.download([signed_url])

        except Exception as e:
            print(f"Error processing video: {str(e)}")
            try:
                # Fallback approach using direct ffmpeg
                print("\nTrying fallback approach...")
                minimal_opts = {
                    'format': 'best',
                    'outtmpl': 'downloaded_video.mp4',
                    'quiet': False,
                    'prefer_ffmpeg': True,
                    'external_downloader': 'ffmpeg',
                    'external_downloader_args': {
                        'ffmpeg_i': ['-headers', 'Accept: */*']
                    },
                    'http_headers': segment_headers
                }
                with YoutubeDL(minimal_opts) as ydl:
                    ydl.download([signed_url])
            except Exception as e2:
                print(f"Fallback approach failed: {str(e2)}")

if __name__ == "__main__":
    # Path to text file containing video URLs
    video_list = "src/video_list.txt"
    
    # Your authentication token
    auth_token = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Mzk1OTUxNDgsImV4cCI6MTczOTYwNTk0OCwia2V5Ijoia2V5MSIsImh0dHBzOi8vbWVkaWEtcGxhdGZvcm0uc3F1YXJlc3BhY2UuY29tL2Fzc2V0LXZpc2liaWxpdHkiOiI3MTlhZjBjZi0zM2IwLTNjYWItOGRlOC0yYmZlOWFhOGRiYTIiLCJodHRwczovL21lZGlhLXBsYXRmb3JtLnNxdWFyZXNwYWNlLmNvbS9saWJyYXJ5LWlkIjoiNjQ4MGZmNTIzMDhlZTg0YzYxMzFmYTFhIn0.Kp4mH_YguI9trUleXdtBZ7eBNov4I0wYI5Axbllys4s"
    
    # Your cookies string
    cookies_str = "crumb=BQX7mX94P7sNZTdiNTc3MWM5ZmFkNzM2MmNmYjQyOWZmNjg5OGZk; SiteUserSecureAuthToken=MXxlZDc3ZDdlMi0zMjBiLTRiNWEtYTlkNi03ODEzYjNhYjRlNWF8SFlPXzFaQ1A4bHk3YWc1ZWRwc2cxdTQ5azdCZ1gwOVNsQUJlaENNQkxmbC10NjlwODhqVDV4R3pOSGQtWUVMOA"
    
    download_squarespace_videos(video_list, auth_token, cookies_str)
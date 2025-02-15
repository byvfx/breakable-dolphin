from yt_dlp import YoutubeDL
import m3u8
import requests
from urllib.parse import urljoin
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SquarespaceVideoDownloader:
    def __init__(self):
        self.cookies_str = os.getenv("COOKIES_STR")
        self.csrf_token = os.getenv("CSRF_TOKEN")
        self.base_url = os.getenv("BASE_URL")  # Default value if not set
        self.cookies = self._parse_cookies(self.cookies_str)
        self.session = self._create_session()
        
    def _parse_cookies(self, cookies_str):
        cookies = {}
        for cookie in cookies_str.split('; '):
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name] = value
        return cookies

    def _create_session(self):
        """Create a new session with proper headers and cookies"""
        session = requests.Session()
        
        # Update headers
        session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
            'origin': self.base_url,
            'referer': f"{self.base_url}/cloud-simulation-course/intro",
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-csrf-token': self.csrf_token
        })
        
        # Set cookies
        requests.utils.add_dict_to_cookiejar(session.cookies, self.cookies)
        
        return session

    def get_auth_token(self):
        """Get fresh authorization token with retry logic"""
        auth_url = f"{self.base_url}/api/media/auth/v1/asset/authorization"
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(auth_url)
                response.raise_for_status()
                auth_data = response.json()
                
                if 'token' in auth_data:
                    print("Successfully obtained auth token")
                    return auth_data['token']
                else:
                    print(f"Token not found in response: {auth_data}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    # Refresh session for next attempt
                    self.session = self._create_session()
                    retry_delay *= 2  # Exponential backoff
                continue
                
        print("Failed to get authorization token after all retries")
        return None

    def download_video(self, playlist_url, output_filename):
        """Download video with improved error handling"""
        max_auth_retries = 2
        
        for auth_attempt in range(max_auth_retries):
            try:
                # Get fresh auth token
                auth_token = self.get_auth_token()
                if not auth_token:
                    if auth_attempt < max_auth_retries - 1:
                        print("Retrying with fresh session...")
                        self.session = self._create_session()
                        continue
                    return False

                # Headers for m3u8 requests
                m3u8_headers = {
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'origin': self.base_url,
                    'referer': f"{self.base_url}/",
                    'authorization': f'Bearer {auth_token}',
                    'user-agent': self.session.headers['user-agent']
                }

                # Get main playlist
                print("Requesting playlist...")
                response = requests.get(playlist_url, headers=m3u8_headers)
                response.raise_for_status()
                main_playlist = m3u8.loads(response.text)

                if main_playlist.playlists:
                    # Find highest quality stream
                    max_bandwidth = max(p.stream_info.bandwidth for p in main_playlist.playlists)
                    best_playlist = next(p for p in main_playlist.playlists if p.stream_info.bandwidth == max_bandwidth)
                    variant_url = urljoin(playlist_url, best_playlist.uri)
                    print(f"Selected quality: {best_playlist.stream_info.resolution}, Bandwidth: {best_playlist.stream_info.bandwidth}")

                    # Configure yt-dlp
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_filename,
                        'quiet': False,
                        'verbose': True,
                        'prefer_ffmpeg': True,
                        'external_downloader': 'ffmpeg',
                        'external_downloader_args': {
                            'ffmpeg_i': [
                                '-headers',
                                '\n'.join([
                                    f'Authorization: Bearer {auth_token}',
                                    'Accept: */*',
                                    'Origin: BASE_URL',
                                    'Referer: BASE_URL'
                                ])
                            ]
                        },
                        'http_headers': m3u8_headers,
                        'hls_prefer_ffmpeg': True,
                        'hls_use_mpegts': True
                    }

                    # Download using yt-dlp
                    with YoutubeDL(ydl_opts) as ydl:
                        print(f"Downloading variant playlist: {variant_url}")
                        ydl.download([variant_url])
                        return True
                else:
                    print("No variant streams found in playlist")
                    return False

            except Exception as e:
                print(f"Error during download attempt {auth_attempt + 1}: {str(e)}")
                if auth_attempt < max_auth_retries - 1:
                    print("Retrying with fresh session...")
                    time.sleep(2)
                    self.session = self._create_session()
                    continue
                return False

def main():
    # Instantiate the downloader - it will load settings from the environment
    downloader = SquarespaceVideoDownloader()
    
    try:
        with open('src/video_urls.txt', 'r') as f:
            video_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("Error: video_urls.txt not found!")
        return
    
    if not video_urls:
        print("No URLs found in video_urls.txt")
        return

    for i, url in enumerate(video_urls, 1):
        print(f"\nProcessing video {i} of {len(video_urls)}")
        print(f"URL: {url}")
        
        output_filename = f"video_{i:03d}.mp4"
        
        if downloader.download_video(url, output_filename):
            print(f"Successfully downloaded video {i} as {output_filename}")
        else:
            print(f"Failed to download video {i}")
        
        if i < len(video_urls):
            print("Waiting 5 seconds before next download...")
            time.sleep(5)

if __name__ == "__main__":
    main()
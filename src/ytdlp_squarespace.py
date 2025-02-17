from yt_dlp import YoutubeDL
import m3u8
import requests
from urllib.parse import urljoin
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SquarespaceVideoDownloader:
    def __init__(self):
        # Previous initialization code remains the same
        self.base_url = os.getenv('BASE_URL')
        if not self.base_url:
            raise ValueError("BASE_URL environment variable is not set")
            
        cookies_str = os.getenv('COOKIES_STR')
        if not cookies_str:
            raise ValueError("COOKIES_STR environment variable is not set")
        self.cookies = self._parse_cookies(cookies_str)
        
        self.csrf_token = os.getenv('CSRF_TOKEN')
        if not self.csrf_token:
            raise ValueError("CSRF_TOKEN environment variable is not set")
            
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
        
        session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'origin': self.base_url,
            'referer': f"{self.base_url}/cloud-simulation-course/intro",
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-csrf-token': self.csrf_token
        })
        
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
                    self.session = self._create_session()
                    retry_delay *= 2
                continue
                
        print("Failed to get authorization token after all retries")
        return None

    def download_video(self, playlist_url, output_filename):
        """Download video with improved audio handling"""
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
                print("Requesting master playlist...")
                response = requests.get(playlist_url, headers=m3u8_headers)
                response.raise_for_status()
                main_playlist = m3u8.loads(response.text)

                if not main_playlist.is_endlist and not main_playlist.playlists:
                    print("Invalid or empty master playlist")
                    return False

                # Configure yt-dlp with improved options
                ydl_opts = {
                    'format': 'bv*+ba/b',  # Modified format selection
                    'outtmpl': output_filename,
                    'quiet': False,
                    'verbose': True,
                    'prefer_ffmpeg': True,
                    'merge_output_format': 'mp4',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                    'external_downloader_args': {
                        'ffmpeg_i': [
                            '-headers',
                            '\n'.join([
                                f'Authorization: Bearer {auth_token}',
                                'Accept: */*',
                                f'Origin: {self.base_url}',
                                f'Referer: {self.base_url}/',
                                'User-Agent: ' + self.session.headers['user-agent']
                            ]),
                            '-allowed_extensions', 'ALL'
                        ]
                    },
                    'http_headers': m3u8_headers,
                    'hls_prefer_ffmpeg': True,
                    'hls_use_mpegts': True,
                    'fragment_retries': 10,
                    'retries': 10
                }

                # Download using yt-dlp
                with YoutubeDL(ydl_opts) as ydl:
                    print(f"Downloading from master playlist: {playlist_url}")
                    ydl.download([playlist_url])
                    return True

            except Exception as e:
                print(f"Error during download attempt {auth_attempt + 1}: {str(e)}")
                if auth_attempt < max_auth_retries - 1:
                    print("Retrying with fresh session...")
                    time.sleep(2)
                    self.session = self._create_session()
                    continue
                return False

def main():
    # Initialize downloader with environment variables
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
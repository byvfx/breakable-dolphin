from yt_dlp import YoutubeDL
import m3u8
import requests
import json
from urllib.parse import urljoin

class SquarespaceVideoDownloader:
    def __init__(self, cookies_str, csrf_token):
        self.cookies = self._parse_cookies(cookies_str)
        self.csrf_token = csrf_token
        self.session = requests.Session()
        self.base_url = "https://www.breakyourcrayons.com"
        
        # Set up session headers
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
            'origin': 'https://www.breakyourcrayons.com',
            'referer': 'https://www.breakyourcrayons.com/cloud-simulation-course/intro',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-csrf-token': csrf_token
        })
        
        # Set cookies
        self.session.cookies.update(self.cookies)

    def _parse_cookies(self, cookies_str):
        cookies = {}
        for cookie in cookies_str.split('; '):
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name] = value
        return cookies

    def get_auth_token(self):
        """Get fresh authorization token"""
        auth_url = f"{self.base_url}/api/media/auth/v1/asset/authorization"
        try:
            response = self.session.get(auth_url)
            response.raise_for_status()
            auth_data = response.json()
            print("Successfully obtained auth token")
            return auth_data.get('token')  # Or handle the actual response structure
        except Exception as e:
            print(f"Error getting auth token: {str(e)}")
            return None

    def download_video(self, playlist_url, output_filename="downloaded_video.mp4"):
        """Download video using the complete authorization flow"""
        try:
            # Get fresh auth token
            auth_token = self.get_auth_token()
            if not auth_token:
                print("Failed to get authorization token")
                return False

            # Headers for m3u8 requests
            m3u8_headers = {
                **self.session.headers,
                'authorization': f'Bearer {auth_token}',
                'sec-fetch-site': 'cross-site'
            }

            # Get main playlist
            response = requests.get(playlist_url, headers=m3u8_headers)
            response.raise_for_status()
            main_playlist = m3u8.loads(response.text)

            # Find highest quality stream
            if main_playlist.playlists:
                max_bandwidth = max(p.stream_info.bandwidth for p in main_playlist.playlists)
                best_playlist = next(p for p in main_playlist.playlists if p.stream_info.bandwidth == max_bandwidth)
                variant_url = urljoin(playlist_url, best_playlist.uri)
                print(f"Selected quality: {best_playlist.stream_info.resolution}, Bandwidth: {best_playlist.stream_info.bandwidth}")

                # Configure yt-dlp for download
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
                            f'Authorization: Bearer {auth_token}\r\n' +
                            'Accept: */*\r\n' +
                            'Accept-Language: en-US,en;q=0.9\r\n' +
                            'Origin: https://www.breakyourcrayons.com\r\n' +
                            'Referer: https://www.breakyourcrayons.com/\r\n'
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
            print(f"Error downloading video: {str(e)}")
            return False

def main():
    # Your cookies string
    cookies_str = "crumb=BQX7mX94P7sNZTdiNTc3MWM5ZmFkNzM2MmNmYjQyOWZmNjg5OGZk; SiteUserSecureAuthToken=MXxlZDc3ZDdlMi0zMjBiLTRiNWEtYTlkNi03ODEzYjNhYjRlNWF8SFlPXzFaQ1A4bHk3YWc1ZWRwc2cxdTQ5azdCZ1gwOVNsQUJlaENNQkxmbC10NjlwODhqVDV4R3pOSGQtWUVMOA"
    
    # CSRF token
    csrf_token = "BQX7mX94P7sNZTdiNTc3MWM5ZmFkNzM2MmNmYjQyOWZmNjg5OGZk"
    
    # Create downloader instance
    downloader = SquarespaceVideoDownloader(cookies_str, csrf_token)
    
    # Video URL
    video_url = "https://video.squarespace-cdn.com/content/v1/6480ff52308ee84c6131fa1a/d7551605-7506-4fc7-8dc1-3b5a6e86b7ba/playlist.m3u8"
    
    # Download video
    if downloader.download_video(video_url):
        print("Video downloaded successfully!")
    else:
        print("Failed to download video")

if __name__ == "__main__":
    main()
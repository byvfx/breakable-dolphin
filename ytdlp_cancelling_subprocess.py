import subprocess
import sys
import time

def run_download(url):
    # Command to run yt-dlp with specified options
    command = [
        'yt-dlp',
        url,
        '--output', '%(title)s.%(ext)s',
        '--format', 'best',
    ]

    # Start the download process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True  # For text output instead of bytes
    )

    print(f"Starting download of {url}...")
    
    # Stream output in real-time
    while process.poll() is None:  # While process is running
        output = process.stdout.readline().strip()
        if output:
            print(output)
        
        # Check for user input to cancel (non-blocking check could be added if needed)
        try:
            user_input = input("Type '1' to stop the download: ").strip().lower()
            if user_input == '1':
                print("Cancelling download...")
                process.terminate()  # Send termination signal
                process.wait()  # Wait for process to fully exit
                print("Download cancelled.")
                return False
        except EOFError:
            # Handle Ctrl+D or Ctrl+Z gracefully (input not available in some IDEs)
            pass

    # Check if the process ended naturally
    if process.returncode == 0:
        print("Download completed successfully!")
        return True
    else:
        # Print any errors if the process failed
        error_output = process.stderr.read().1strip()
        if error_output:
            print(f"Download failed with error: {error_output}")
        else:
            print("Download terminated with an unknown error.")
        return False

def main():
    video_url = "https://www.youtube.com/watch?v=sX8NpVvP5_8"

    print("Press Ctrl+C at any time to exit the script.")

    try:
        success = run_download(video_url)
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")
        sys.exit(0)
    except FileNotFoundError:
        print("Error: yt-dlp not found. Please install it and ensure it's in your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
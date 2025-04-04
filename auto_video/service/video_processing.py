import logging
import requests
from yt_dlp import YoutubeDL
import subprocess
import datetime

# Create a logger instance
logger = logging.getLogger(__name__)

def download_video(url):
    # generate file name by time
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    original_filename = f'data/video-{timestamp}.mp4'
    reencoded_filename = f'data/video-encode-{timestamp}.mp4'

    logger.info(f"Downloading video from URL: {url}")
    # Download the video from the URL
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': original_filename,
            'merge_output_format': 'mp4',
            'no_check_certificates': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'extract_flat': False,
            'force_generic_extractor': False,
            'cookiesfrombrowser': ('chrome',),  # This will use cookies from Chrome if available
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Re-encode the video to ensure compatibility
        logger.info("Re-encoding video for compatibility...")
        
        cmd = ['ffmpeg', '-i', original_filename, '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', reencoded_filename]
        subprocess.run(cmd, check=True)

        logger.info(f"Video re-encoded successfully and saved as: {reencoded_filename}")

        # Delete the original video file
        logger.info("Deleting the original video file...")
        subprocess.run(['rm', original_filename])
        
    except Exception as e:
        logger.error(f"Failed to download the video: {e}")
    pass


def upload_video(url):
  
    pass
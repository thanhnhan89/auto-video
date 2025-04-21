import logging
import requests
from yt_dlp import YoutubeDL
import subprocess
import datetime
import re
import os

# Create a logger instance
logger = logging.getLogger(__name__)

def download_video(url):
    # generate file name by time
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Get video title first
    try:
        with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', '')
            # Clean the title to make it filesystem-friendly
            video_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
            video_title = video_title.strip()
    except Exception as e:
        logger.error(f"Failed to extract video title: {e}")
        video_title = f"video-{timestamp}"
    
    original_filename = f'data/{video_title}-{timestamp}.mp4'
    reencoded_filename = f'data/{video_title}-encode-{timestamp}.mp4'

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

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
        
        # Return the file path and clean filename for browser download
        download_filename = f'{video_title}.mp4'
        return {
            'file_path': reencoded_filename,
            'download_filename': download_filename
        }
        
    except Exception as e:
        logger.error(f"Failed to download the video: {e}")
        return None


def upload_video(url):
  
    pass
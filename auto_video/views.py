from django.http import HttpResponse
from django.shortcuts import render
import logging
import requests
from pytube import YouTube
from yt_dlp import YoutubeDL
import subprocess
import datetime

# Create a logger instance
logger = logging.getLogger(__name__)

def my_new_page(request):

    # url = 'https://www.youtube.com/watch?v=58EIyxTSRwg'
    url = 'https://www.youtube.com/shorts/i4Kt7p0Y29g'

    # Download the video from the URL
    # download_video(url)


    # return HttpResponse("Welcome to my new page!")
    return render(request, '/templates/new_page.html')

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
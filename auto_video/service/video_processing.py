import logging
import requests
from yt_dlp import YoutubeDL
import subprocess
import datetime
import re
import os
import shutil
import sys

# Create a logger instance
logger = logging.getLogger(__name__)

def check_disk_space(path, required_space_mb=100):
    """Check if there's enough disk space available"""
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (1024 * 1024)  # Convert to MB
        logger.info(f"Available disk space: {free_mb}MB")
        return free_mb >= required_space_mb
    except Exception as e:
        logger.error(f"Failed to check disk space: {str(e)}")
        return False

def list_available_formats(url):
    """List all available formats for a video URL"""
    try:
        with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            logger.info("Available formats:")
            for f in formats:
                logger.info(f"Format: {f.get('format_id')} - {f.get('ext')} - {f.get('format_note', '')} - {f.get('resolution', '')}")
            return formats
    except Exception as e:
        logger.error(f"Failed to list formats: {str(e)}")
        return None

def encode_video(input_file, output_file):
    """Encode video to ensure compatibility across platforms"""
    try:
        # FFmpeg command for encoding with compatibility settings
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',  # Use H.264 codec for maximum compatibility
            '-preset', 'medium',  # Balance between quality and encoding speed
            '-crf', '23',  # Constant Rate Factor (18-28 is good, lower is better quality)
            '-c:a', 'aac',  # Use AAC audio codec
            '-b:a', '128k',  # Audio bitrate
            '-movflags', '+faststart',  # Enable fast start for web playback
            '-pix_fmt', 'yuv420p',  # Pixel format for better compatibility
            output_file
        ]
        
        logger.info("Starting video encoding...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Video encoding completed successfully")
            return True
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error during video encoding: {str(e)}")
        return False

def download_video(url):
    logger.info(f"Starting download for URL: {url}")
    
    # Generate timestamp for unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Set up filenames
    temp_filename = f'data/temp-{timestamp}.mp4'
    final_filename = f'data/video-{timestamp}.mp4'
    
    # First try to get available formats
    try:
        formats = list_available_formats(url)
        if not formats:
            logger.error("Could not retrieve available formats")
            return None
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        formats = []
    
    # Try different quality levels with improved format strings
    quality_options = [
        # Option 1: High quality (720p or better)
        {
            'format': 'bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=720]+bestaudio/best[height>=720]/bestvideo+bestaudio/best',
            'name': '720p or higher'
        },
        # Option 2: Medium quality (480p)
        {
            'format': 'bestvideo[height>=480][height<720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=480][height<720]+bestaudio/best[height>=480][height<720]/bestvideo+bestaudio/best',
            'name': '480p or higher'
        },
        # Option 3: Any quality 
        {
            'format': 'bestvideo+bestaudio/best',
            'name': 'Any quality'
        },
        # Option 4: Format 18 (often 360p MP4)
        {
            'format': '18/bestvideo[height<=360]+bestaudio/best[height<=360]/best',
            'name': '360p MP4'
        }
    ]
    
    for quality in quality_options:
        try:
            logger.info(f"Attempting download with {quality['name']} quality...")
            
            ydl_opts = {
                'format': quality['format'],
                'outtmpl': temp_filename,
                'quiet': False,
                'no_warnings': False,
                'verbose': True,
                'merge_output_format': 'mp4',
                'ignoreerrors': True,  # Continue on download errors
                'noplaylist': True,    # Only download single video, not playlist
            }
            
            # Download the video
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            # Check if file was downloaded successfully
            if os.path.exists(temp_filename):
                file_size = os.path.getsize(temp_filename)
                if file_size > 0:
                    logger.info(f"Successfully downloaded video with {quality['name']} quality: {temp_filename} ({file_size} bytes)")
                    
                    # Encode the video for compatibility
                    if encode_video(temp_filename, final_filename):
                        # Clean up temporary file
                        os.remove(temp_filename)
                        return {
                            'file_path': final_filename,
                            'download_filename': f'video-{timestamp}.mp4'
                        }
                    else:
                        logger.error("Video encoding failed")
                        # If encoding fails, return the original file
                        os.rename(temp_filename, final_filename)
                        return {
                            'file_path': final_filename,
                            'download_filename': f'video-{timestamp}.mp4'
                        }
                else:
                    logger.warning(f"Downloaded file is empty with {quality['name']} quality")
                    os.remove(temp_filename)
            else:
                logger.warning(f"Download completed but file not found with {quality['name']} quality")
                
        except Exception as e:
            logger.error(f"Error downloading with {quality['name']} quality: {str(e)}")
            # Clean up any partial download
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            continue
    
    # Last resort: try each format ID directly
    if formats:
        logger.info("Trying individual format IDs as last resort...")
        for fmt in formats:
            format_id = fmt.get('format_id')
            if not format_id:
                continue
                
            try:
                logger.info(f"Attempting download with format ID: {format_id}")
                
                ydl_opts = {
                    'format': format_id,
                    'outtmpl': temp_filename,
                    'quiet': False,
                    'merge_output_format': 'mp4',
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                    logger.info(f"Successfully downloaded with format ID {format_id}")
                    
                    # Encode the video for compatibility
                    if encode_video(temp_filename, final_filename):
                        os.remove(temp_filename)
                        return {
                            'file_path': final_filename,
                            'download_filename': f'video-{timestamp}.mp4'
                        }
                    else:
                        os.rename(temp_filename, final_filename)
                        return {
                            'file_path': final_filename,
                            'download_filename': f'video-{timestamp}.mp4'
                        }
                else:
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
            except Exception as e:
                logger.error(f"Error downloading with format ID {format_id}: {str(e)}")
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                continue
    
    logger.error("All download attempts failed")
    return None

def upload_video(url):
  
    pass
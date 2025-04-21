from django.http import HttpResponse, FileResponse
from django.shortcuts import render
import logging
import os
from .forms import VideoForm
from .service.video_processing import download_video

# Create a logger instance
logger = logging.getLogger(__name__)

def video_page(request):
    # Download the video from the URL
    if(request.method == 'POST'):
        form = VideoForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Download the video from the URL
            result = download_video(url)
            
            if result:
                file_path = result['file_path']
                download_filename = result['download_filename']
                
                # Check if file exists
                if os.path.exists(file_path):
                    # Serve the file for download
                    response = FileResponse(
                        open(file_path, 'rb'),
                        as_attachment=True,
                        filename=download_filename
                    )
                    
                    # Set content type for video
                    response['Content-Type'] = 'video/mp4'
                    
                    # Cleanup: optionally delete the file after serving
                    # Uncomment if you want to delete the file after serving
                    # def delete_file_after_response(file_path=file_path):
                    #     if os.path.exists(file_path):
                    #         os.remove(file_path)
                    # response.close = delete_file_after_response
                    
                    return response
                else:
                    return HttpResponse("Error: File not found", status=404)
            else:
                return HttpResponse("Error: Could not download the video", status=500)

    # case when request is GET then show form
    form = VideoForm()
    
    return render(request, 'video_page.html', {'form': form})


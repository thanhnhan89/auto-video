from django.http import HttpResponse
from django.shortcuts import render
import logging
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
            download_video(url)

            return HttpResponse("Video downloaded successfully!")

    # case when request is GET then show form
    form = VideoForm()
    
    return render(request, 'video_page.html', {'form': form})


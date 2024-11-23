# downloader/views.py
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
import yt_dlp
import os
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def download_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_url = data.get('url')
            if video_url:
                ydl_opts = {
                    'format': 'best',  # Download best quality
                    'outtmpl': '%(title)s.%(ext)s',
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(video_url, download=True)
                        video_title = ydl.prepare_filename(info_dict)
                    
                    if os.path.exists(video_title):
                        response = FileResponse(open(video_title, 'rb'))
                        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_title)}"'
                        return response
                    else:
                        return JsonResponse({'status': 'error', 'message': 'File not found after download'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})
            else:
                return JsonResponse({'status': 'error', 'message': 'URL not provided'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

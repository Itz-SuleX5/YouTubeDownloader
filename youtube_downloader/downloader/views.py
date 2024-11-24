# downloader/views.py
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from pytube import YouTube
import os
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path
import tempfile
import shutil

# Crear un directorio temporal para las descargas
DOWNLOAD_DIR = Path(__file__).parent.parent / 'temp'
DOWNLOAD_DIR.mkdir(exist_ok=True)

@csrf_exempt
def download_video(request):
    # Agregar logging para debug
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': f'Method {request.method} not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        video_url = data.get('url')

        if not video_url:
            return JsonResponse({'status': 'error', 'message': 'URL not provided'}, status=400)

        # Crear un directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Crear objeto YouTube
                yt = YouTube(video_url)
                
                # Obtener el stream con la mejor resolución
                video = yt.streams.get_highest_resolution()
                
                # Descargar el video
                video_path = video.download(output_path=temp_dir)
                
                if os.path.exists(video_path):
                    # Abrir y enviar el archivo
                    response = FileResponse(
                        open(video_path, 'rb'),
                        as_attachment=True,
                        filename=os.path.basename(video_path)
                    )
                    return response
                else:
                    return JsonResponse({'status': 'error', 'message': 'File not found after download'}, status=404)

            except Exception as e:
                print(f"Download error: {str(e)}")  # Agregar logging
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"General error: {str(e)}")  # Agregar logging
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

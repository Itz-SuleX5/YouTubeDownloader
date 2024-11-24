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
import random

# Crear un directorio temporal para las descargas
DOWNLOAD_DIR = Path(__file__).parent.parent / 'temp'
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Lista de user agents comunes
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
]

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
                # Configurar YouTube con un user agent aleatorio
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Keep-Alive': 'timeout=15, max=100',
                    'Connection': 'keep-alive',
                }
                
                # Crear objeto YouTube con las opciones personalizadas
                yt = YouTube(
                    video_url,
                    use_oauth=False,
                    allow_oauth_cache=True,
                    on_progress_callback=lambda stream, chunk, bytes_remaining: print(f"Downloading... {(1 - bytes_remaining/stream.filesize)*100}%")
                )
                
                # Configurar el user agent
                yt.headers = headers
                
                print(f"Video title: {yt.title}")
                print(f"Available streams: {[stream.resolution for stream in yt.streams.filter(progressive=True)]}")
                
                # Obtener el stream con la mejor resolución (progressive=True para obtener video+audio juntos)
                video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                
                if not video:
                    return JsonResponse({'status': 'error', 'message': 'No suitable video stream found'}, status=404)
                
                print(f"Selected stream: {video.resolution}")
                
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

# downloader/views.py
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
import yt_dlp
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
        format_type = data.get('format', 'mp4')
        quality = data.get('quality', 'highest')

        if not video_url:
            return JsonResponse({'status': 'error', 'message': 'URL not provided'}, status=400)

        # Crear un directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Configurar las opciones de descarga según el formato y calidad
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if format_type == 'mp4' else 'bestaudio[ext=mp3]/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }

                # Si es audio, convertir a MP3
                if format_type == 'mp3':
                    ydl_opts.update({
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })

                # Descargar el video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    video_title = ydl.prepare_filename(info)
                    
                    # Ajustar la extensión si es MP3
                    if format_type == 'mp3':
                        video_title = str(Path(video_title).with_suffix('.mp3'))

                    if os.path.exists(video_title):
                        # Abrir y enviar el archivo
                        response = FileResponse(
                            open(video_title, 'rb'),
                            as_attachment=True,
                            filename=os.path.basename(video_title)
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

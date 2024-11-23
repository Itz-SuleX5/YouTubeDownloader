# downloader/views.py
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
import yt_dlp
import os
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path

# Crear un directorio temporal para las descargas
DOWNLOAD_DIR = Path(__file__).parent.parent / 'temp'
DOWNLOAD_DIR.mkdir(exist_ok=True)

@csrf_exempt
def download_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_url = data.get('url')
            format_type = data.get('format', 'mp4')
            quality = data.get('quality', 'highest')

            if not video_url:
                return JsonResponse({'status': 'error', 'message': 'URL not provided'})

            # Configurar las opciones de descarga según el formato y calidad
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if format_type == 'mp4' else 'bestaudio[ext=mp3]/best',
                'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
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

            try:
                # Descargar el video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    video_title = ydl.prepare_filename(info)
                    
                    # Ajustar la extensión si es MP3
                    if format_type == 'mp3':
                        video_title = str(Path(video_title).with_suffix('.mp3'))

                    if os.path.exists(video_title):
                        # Abrir y enviar el archivo
                        with open(video_title, 'rb') as file:
                            response = HttpResponse(file.read(), content_type='application/octet-stream')
                            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_title)}"'
                            
                            # Eliminar el archivo después de enviarlo
                            try:
                                os.remove(video_title)
                            except Exception as e:
                                print(f"Error removing file: {e}")
                                
                            return response
                    else:
                        return JsonResponse({'status': 'error', 'message': 'File not found after download'})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

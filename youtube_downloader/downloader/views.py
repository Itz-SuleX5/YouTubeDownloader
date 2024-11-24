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
import requests
import time

# Lista de user agents más completa y actualizada
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
]

def get_youtube_page(url):
    """Obtiene la página de YouTube con headers completos"""
    user_agent = random.choice(USER_AGENTS)
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    
    session = requests.Session()
    # Simular comportamiento de navegador
    session.headers.update(headers)
    
    # Hacer una solicitud inicial para obtener cookies
    response = session.get(url, timeout=15)
    cookies = session.cookies.get_dict()
    
    return {'headers': headers, 'cookies': cookies}

@csrf_exempt
def download_video(request):
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
                # Obtener headers y cookies realistas
                browser_data = get_youtube_page(video_url)
                
                # Crear objeto YouTube con configuración mejorada
                yt = YouTube(
                    url=video_url,
                    use_oauth=False,
                    allow_oauth_cache=True
                )
                
                # Configurar headers y cookies
                yt.headers = browser_data['headers']
                yt._http.cookies.update(browser_data['cookies'])
                
                # Agregar un pequeño delay para simular comportamiento humano
                time.sleep(random.uniform(1, 2))
                
                try:
                    # Intentar obtener streams con retry
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            streams = yt.streams.filter(progressive=True, file_extension='mp4')
                            if streams:
                                break
                            time.sleep(random.uniform(1, 2))
                        except Exception as e:
                            if attempt == max_retries - 1:
                                raise e
                            time.sleep(random.uniform(1, 2))
                    
                    if not streams:
                        return JsonResponse({'status': 'error', 'message': 'No suitable video stream found'}, status=404)
                    
                    video = streams.first()
                    if not video:
                        return JsonResponse({'status': 'error', 'message': 'No video stream available'}, status=404)
                    
                    # Generar nombre de archivo
                    output_filename = f"video_{random.randint(1000, 9999)}.mp4"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    # Descargar con retry
                    max_download_retries = 3
                    for attempt in range(max_download_retries):
                        try:
                            video.download(output_path=temp_dir, filename=output_filename)
                            break
                        except Exception as e:
                            if attempt == max_download_retries - 1:
                                raise e
                            time.sleep(random.uniform(1, 2))
                    
                    if os.path.exists(output_path):
                        response = FileResponse(
                            open(output_path, 'rb'),
                            as_attachment=True,
                            filename=output_filename
                        )
                        return response
                    else:
                        return JsonResponse({'status': 'error', 'message': 'File not found after download'}, status=404)
                
                except Exception as e:
                    print(f"Stream error: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': f'Error accessing video streams: {str(e)}'}, status=500)

            except Exception as e:
                print(f"Download error: {str(e)}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"General error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

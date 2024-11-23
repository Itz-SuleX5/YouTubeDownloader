from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pytube import YouTube
import os
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto a tu dominio frontend específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str
    format: Optional[str] = "mp4"
    quality: Optional[str] = "highest"

@app.get("/")
def read_root():
    return {"message": "YouTube Downloader API is running"}

@app.post("/download")
async def download_video(video_request: VideoRequest):
    try:
        yt = YouTube(video_request.url)
        if video_request.format == "mp4":
            if video_request.quality == "highest":
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.get_lowest_resolution()
        elif video_request.format == "mp3":
            stream = yt.streams.filter(only_audio=True).first()
        
        # Crear directorio temporal si no existe
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        # Descargar el archivo
        file_path = stream.download(output_path="temp")
        
        # Obtener información del video
        return {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

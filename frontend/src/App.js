import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Search,
  Mic,
} from "lucide-react";

import "./index.css";

function App() {
  const [videoUrl, setVideoUrl] = useState("");
  const [format, setFormat] = useState("video");
  const [quality, setQuality] = useState("1080");
  const [statusMessage, setStatusMessage] = useState("");
  const [player, setPlayer] = useState(null);

  useEffect(() => {
    let script;
    if (!window.YT) {
      script = document.createElement("script");
      script.src = "https://www.youtube.com/iframe_api";
      
      window.onYouTubeIframeAPIReady = () => {
        console.log("YouTube API is ready");
        window.YT_API_READY = true;
      };
      
      document.body.appendChild(script);
    }

    return () => {
      // Clean up script tag if it exists
      if (player) {
        player.destroy();
        setPlayer(null);
      }
      // Clean up global variables
      delete window.onYouTubeIframeAPIReady;
      delete window.youtubePlayer;
    };
  }, []);
  
  // Handle player initialization when URL changes
  useEffect(() => {
    if (!videoUrl) return;
    
    const videoId = extractVideoId(videoUrl);
    if (!videoId) return;

    let timeoutId = null;

    // If we have an existing player, just load the new video
    if (player) {
      try {
        player.cueVideoById(videoId);
        return;
      } catch (error) {
        console.error("Error loading video:", error);
        // If loading fails, we'll create a new player below
      }
    }

    const initializePlayer = () => {
      if (!window.YT || !window.YT.Player) {
        // If API is not ready yet, wait for it
        timeoutId = setTimeout(initializePlayer, 100);
        return;
      }

      try {
        console.log("Creating new YouTube player...");
        // Clean up existing player if any
        if (player) {
          player.destroy();
          setPlayer(null);
        }
        // Create new player instance
        const newPlayer = new window.YT.Player("youtube-player", {
          videoId: videoId,
          width: "100%",
          height: "100%",
          playerVars: {
            autoplay: 0,
            controls: 1,
            modestbranding: 1,
          },
          events: {
            onReady: (event) => {
              console.log("Player ready with video");
              setPlayer(event.target);
            },
            onError: (error) => {
              console.error("YouTube player error:", error);
            }
          }
        });
      } catch (error) {
        console.error("Error creating YouTube player:", error);
        // If creation fails, try again after a delay
        timeoutId = setTimeout(initializePlayer, 100);
      }
    };

    // Start initialization process
    initializePlayer();

    // Cleanup function
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [videoUrl]); // Only depend on videoUrl, not player

  const extractVideoId = (url) => {
    // Regular expression to extract YouTube video ID from various URL formats
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const handleUrlChange = (e) => {
    const url = e.target.value;
    setVideoUrl(url);
  };

  const handleDownload = async () => {
    if (!videoUrl) {
      setStatusMessage("Por favor, ingresa una URL de YouTube.");
      return;
    }

    try {
      setStatusMessage("Iniciando descarga...");
      const response = await axios.post("http://localhost:8000/downloader/download/", {
        url: videoUrl,
        format: format,
        quality: quality,
      }, {
        responseType: "blob",
      });

      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.setAttribute("download", `video.${format === "video" ? "mp4" : "mp3"}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setStatusMessage("Descarga completada.");
    } catch (error) {
      console.error("Error downloading video:", error);
      setStatusMessage("Error en la descarga. Por favor, intenta nuevamente.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <h1 className="text-3xl font-bold text-center mb-8">YouTube Downloader</h1>
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Video */}
          <div className="lg:order-2">
          <div 
            className="rounded-lg overflow-hidden mb-4 bg-gray-100"
            style={{
              position: 'relative',
              paddingBottom: '56.25%', /* 16:9 */
              height: 0,
            }}
          >
            <div 
              id="youtube-player"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
              }}
            ></div>
          </div>
        </div>


          {/* Formulario */}
          <div className="space-y-6 lg:order-1">
            <div className="relative">
              <input
                type="text"
                placeholder="Enter YouTube URL here"
                value={videoUrl}
                onChange={handleUrlChange}
                className="w-full pl-10 pr-10 py-2 text-lg border rounded"
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <button
                type="button"
                className="absolute right-3 top-1/2 transform -translate-y-1/2"
              >
                <Mic className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full border rounded px-3 py-2"
              >
                <option value="video">Video</option>
                <option value="audio">Audio</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Resolution/Quality</label>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="w-full border rounded px-3 py-2"
              >
                <option value="1080">1080p</option>
                <option value="720">720p</option>
                <option value="480">480p</option>
                <option value="360">360p</option>
                <option value="240">240p</option>
                <option value="144">144p</option>
              </select>
            </div>

            <button
              onClick={handleDownload}
              className="w-full bg-blue-500 text-white py-2 rounded font-medium"
            >
              Descargar Video
            </button>
            <p className="text-center text-sm text-gray-500 mt-4">{statusMessage}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
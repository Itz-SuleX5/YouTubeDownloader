import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Search,
  Mic,
} from "lucide-react";

import "./index.css";

// Obtener la URL de la API desde las variables de entorno o usar un valor por defecto
const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');

function App() {
  const [videoUrl, setVideoUrl] = useState("");
  const [format, setFormat] = useState("mp4");
  const [quality, setQuality] = useState("highest");
  const [statusMessage, setStatusMessage] = useState("");
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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

  useEffect(() => {
    if (videoUrl) {
      if (player) {
        player.destroy();
      }
      const videoId = extractVideoId(videoUrl);
      if (!videoId) return;

      let timeoutId = null;

      const initializePlayer = () => {
        if (!window.YT || !window.YT.Player) {
          timeoutId = setTimeout(initializePlayer, 100);
          return;
        }

        try {
          console.log("Creating new YouTube player...");
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
          timeoutId = setTimeout(initializePlayer, 100);
        }
      };

      initializePlayer();

      return () => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      };
    }
  }, [videoUrl, player]);

  const handleVideoUrlChange = (e) => {
    const url = e.target.value;
    setVideoUrl(url);
    
    if (player) {
      player.destroy();
    }
    
    if (url) {
      const videoId = extractVideoId(url);
      if (videoId) {
        const initializePlayer = () => {
          if (!window.YT || !window.YT.Player) {
            setTimeout(initializePlayer, 100);
            return;
          }

          try {
            console.log("Creating new YouTube player...");
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
            setTimeout(initializePlayer, 100);
          }
        };

        initializePlayer();
      }
    }
  };

  useEffect(() => {
    return () => {
      if (player) {
        player.destroy();
      }
    };
  }, [player]);

  const extractVideoId = (url) => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu.be\/|youtube.com\/embed\/)([^&?]+)/,
    ];
    const match = patterns.find((pattern) => pattern.test(url));
    return match && match[1].length === 11 ? match[1] : null;
  };

  const handleDownload = async () => {
    if (!videoUrl) {
      setStatusMessage("Por favor, ingresa una URL de YouTube.");
      return;
    }

    try {
      setStatusMessage("Iniciando descarga...");
      setLoading(true);
      setError(null);
      setResult(null);

      const response = await axios.post(`${API_URL}/downloader/download/`, {
        url: videoUrl
      }, {
        responseType: "blob",
      });

      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.setAttribute("download", `video.${format}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setStatusMessage("Descarga completada.");
      setLoading(false);
    } catch (error) {
      console.error("Error downloading video:", error);
      setStatusMessage("Error en la descarga. Por favor, intenta nuevamente.");
      setError(error.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center">
      <div className="container mx-auto px-4">
        <div className="relative px-4 py-10 bg-white shadow rounded-3xl sm:p-10">
          <div className="w-full">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
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
                        onChange={handleVideoUrlChange}
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
                        <option value="mp4">Video (MP4)</option>
                        <option value="mp3">Audio (MP3)</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium">Resolution/Quality</label>
                      <select
                        value={quality}
                        onChange={(e) => setQuality(e.target.value)}
                        className="w-full border rounded px-3 py-2"
                      >
                        <option value="highest">Highest Quality</option>
                        <option value="lowest">Lowest Quality</option>
                      </select>
                    </div>

                    <button
                      onClick={handleDownload}
                      disabled={loading}
                      className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                      {loading ? 'Downloading...' : 'Descargar Video'}
                    </button>
                    <p className="text-center text-sm text-gray-500 mt-4">{statusMessage}</p>
                    {error && (
                      <div className="mt-4 text-red-600">
                        Error: {error}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
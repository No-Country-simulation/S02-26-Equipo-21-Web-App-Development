import React, { useState, useCallback, useEffect } from "react";
import { FileUpload, VideoList, Notification } from "./components";
import { videoApi, VideoResponse } from "./services/api";
import { Video, NotificationState } from "./types";
import "./App.css";

const App: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [notification, setNotification] = useState<NotificationState | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);

  // Load videos from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("videos");
    if (saved) {
      try {
        setVideos(JSON.parse(saved));
      } catch (err) {
        console.error("Error loading videos from localStorage:", err);
      }
    }
  }, []);

  // Save videos to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("videos", JSON.stringify(videos));
  }, [videos]);

  const showNotification = useCallback(
    (
      message: string,
      type: "success" | "error" | "info" | "warning" = "info",
    ) => {
      const id = `notification-${Date.now()}`;
      setNotification({ id, type, message });
    },
    [],
  );

  const handleUploadSuccess = useCallback(
    (videoId: string) => {
      // Add new video to the list
      const newVideo: Video = {
        id: videoId,
        fileName: "Cargando...",
        status: "Pending",
        createdAt: new Date().toISOString(),
      };

      setVideos((prev) => [newVideo, ...prev]);
      showNotification(
        "✓ Video subido exitosamente. Comenzando procesamiento...",
        "success",
      );

      // Fetch the video details immediately
      fetchVideoDetails(videoId);
    },
    [showNotification],
  );

  const fetchVideoDetails = async (id: string) => {
    try {
      const response = await videoApi.getVideoById(id);
      updateVideoInList(response);
    } catch (error) {
      console.error("Error fetching video details:", error);
    }
  };

  const updateVideoInList = (apiVideo: VideoResponse) => {
    setVideos((prev) =>
      prev.map((v) =>
        v.id === apiVideo.id
          ? {
              ...v,
              fileName: apiVideo.fileName,
              status: apiVideo.status,
              createdAt: apiVideo.createdAt,
              completedAt: apiVideo.completedAt,
              errorMessage: apiVideo.errorMessage,
            }
          : v,
      ),
    );
  };

  const handleRefreshVideo = useCallback(
    async (id: string) => {
      try {
        const response = await videoApi.getVideoById(id);
        updateVideoInList(response);

        // Show status update notification if status changed
        const video = videos.find((v) => v.id === id);
        if (video && video.status !== response.status) {
          if (response.status === "Completed") {
            showNotification("✓ Video procesado completamente", "success");
          } else if (response.status === "Failed") {
            showNotification("✕ Error al procesar el video", "error");
          }
        }
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Error al actualizar el video";
        showNotification(message, "error");
      }
    },
    [videos, showNotification],
  );

  const handleLoadPendingVideos = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await videoApi.getPendingVideos();

      // Update or add pending videos
      setVideos((prev) => {
        const updated = [...prev];
        response.forEach((apiVideo) => {
          const index = updated.findIndex((v) => v.id === apiVideo.id);
          const videoToUpdate: Video = {
            id: apiVideo.id,
            fileName: apiVideo.fileName,
            status: apiVideo.status,
            createdAt: apiVideo.createdAt,
            completedAt: apiVideo.completedAt,
            errorMessage: apiVideo.errorMessage,
          };

          if (index >= 0) {
            updated[index] = videoToUpdate;
          } else {
            updated.push(videoToUpdate);
          }
        });
        return updated;
      });

      if (response.length > 0) {
        showNotification(`${response.length} video(s) encontrado(s)`, "info");
      }
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Error al cargar videos pendientes";
      showNotification(message, "error");
    } finally {
      setIsLoading(false);
    }
  }, [showNotification]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎬 Video Shorts Generator</h1>
          <p>Procesa tus videos y crea shorts automáticamente</p>
          <button
            className="btn-load-pending"
            onClick={handleLoadPendingVideos}
            disabled={isLoading}
          >
            {isLoading ? "Cargando..." : "📋 Cargar Videos Pendientes"}
          </button>
        </div>
      </header>

      <main className="app-main">
        <FileUpload
          onUploadSuccess={handleUploadSuccess}
          onError={(msg) => showNotification(msg, "error")}
        />

        <VideoList
          videos={videos}
          onRefresh={handleRefreshVideo}
          onError={(msg) => showNotification(msg, "error")}
        />
      </main>

      {notification && (
        <Notification {...notification} onClose={() => setNotification(null)} />
      )}
    </div>
  );
};

export default App;

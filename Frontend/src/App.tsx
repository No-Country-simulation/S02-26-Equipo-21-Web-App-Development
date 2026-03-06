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
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("videos");
    if (saved) {
      try {
        setVideos(JSON.parse(saved));
      } catch (err) {
        console.error(err);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("videos", JSON.stringify(videos));
  }, [videos]);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await videoApi.getPendingVideos();
        setApiOnline(true);
      } catch {
        setApiOnline(false);
      }
    };
    checkHealth();
  }, []);

  const showNotification = useCallback(
    (
      message: string,
      type: "success" | "error" | "info" | "warning" = "info",
    ) => {
      setNotification({ id: `notification-${Date.now()}`, type, message });
    },
    [],
  );

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

  const handleUploadSuccess = useCallback(
    (videoId: string) => {
      setVideos((prev) => [
        {
          id: videoId,
          fileName: "Cargando...",
          status: "Pending",
          createdAt: new Date().toISOString(),
        },
        ...prev,
      ]);
      showNotification(
        "✓ Video subido exitosamente. Comenzando procesamiento...",
        "success",
      );
      videoApi
        .getVideoById(videoId)
        .then(updateVideoInList)
        .catch(console.error);
    },
    [showNotification],
  );

  const handleRefreshVideo = useCallback(
    async (id: string) => {
      try {
        const response = await videoApi.getVideoById(id);
        updateVideoInList(response);
        const video = videos.find((v) => v.id === id);
        if (video && video.status !== response.status) {
          if (response.status === "Completed")
            showNotification("✓ Video procesado completamente", "success");
          else if (response.status === "Failed")
            showNotification("✕ Error al procesar el video", "error");
        }
      } catch (error) {
        showNotification(
          error instanceof Error ? error.message : "Error al actualizar",
          "error",
        );
      }
    },
    [videos, showNotification],
  );

  const handleLoadPendingVideos = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await videoApi.getPendingVideos();
      setVideos((prev) => {
        const updated = [...prev];
        response.forEach((apiVideo) => {
          const index = updated.findIndex((v) => v.id === apiVideo.id);
          const v: Video = {
            id: apiVideo.id,
            fileName: apiVideo.fileName,
            status: apiVideo.status,
            createdAt: apiVideo.createdAt,
            completedAt: apiVideo.completedAt,
            errorMessage: apiVideo.errorMessage,
          };
          if (index >= 0) updated[index] = v;
          else updated.push(v);
        });
        return updated;
      });
      setApiOnline(true);
      showNotification(
        response.length > 0
          ? `${response.length} video(s) encontrado(s)`
          : "No hay videos pendientes",
        "info",
      );
    } catch (error) {
      setApiOnline(false);
      showNotification(
        error instanceof Error
          ? error.message
          : "Error al cargar videos pendientes",
        "error",
      );
    } finally {
      setIsLoading(false);
    }
  }, [showNotification]);

  const totalVideos = videos.length;
  const completedVideos = videos.filter((v) => v.status === "Completed").length;
  const processingVideos = videos.filter(
    (v) => v.status === "Processing" || v.status === "Pending",
  ).length;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <img src="/logo.png" alt="ShortWave" className="app-logo" />

          <div
            className={`header-status ${apiOnline === false ? "offline" : ""}`}
          >
            <span className="status-dot" />
            {apiOnline === null
              ? "Conectando..."
              : apiOnline
                ? "API Online"
                : "API Offline"}
          </div>

          <div className="header-stats">
            <div className="stat-chip">
              Total <strong>{totalVideos}</strong>
            </div>
            {processingVideos > 0 && (
              <div
                className="stat-chip"
                style={{
                  color: "#d97706",
                  borderColor: "rgba(217,119,6,0.2)",
                  background: "rgba(217,119,6,0.06)",
                }}
              >
                En proceso{" "}
                <strong style={{ color: "#d97706" }}>{processingVideos}</strong>
              </div>
            )}
            {completedVideos > 0 && (
              <div
                className="stat-chip"
                style={{
                  color: "#059669",
                  borderColor: "rgba(5,150,105,0.2)",
                  background: "rgba(5,150,105,0.06)",
                }}
              >
                Completados{" "}
                <strong style={{ color: "#059669" }}>{completedVideos}</strong>
              </div>
            )}
          </div>

          <span className="version-badge">MVP v1.0</span>

          <button
            className="btn-load-pending"
            onClick={handleLoadPendingVideos}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="btn-spinner" />
                Cargando...
              </>
            ) : (
              <>
                <svg
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                >
                  <polyline points="1 4 1 10 7 10" />
                  <path d="M3.51 15a9 9 0 1 0 .49-3.5" />
                </svg>
                Sincronizar
              </>
            )}
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

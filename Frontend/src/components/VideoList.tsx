import React from "react";
import { Video } from "../types";
import { VideoCard } from "./VideoCard";
import { videoApi } from "../services/api";
import "./VideoList.css";

interface VideoListProps {
  videos: Video[];
  onRefresh: (id: string) => void;
  onError: (message: string) => void;
}

export const VideoList: React.FC<VideoListProps> = ({
  videos,
  onRefresh,
  onError,
}) => {
  const completedVideos = videos.filter((v) => v.status === "Completed");
  const processingVideos = videos.filter(
    (v) => v.status === "Processing" || v.status === "Pending",
  );
  const failedVideos = videos.filter((v) => v.status === "Failed");

  const handleDownload = async (id: string) => {
    try {
      const blob = await videoApi.downloadVideo(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `video-${id.substring(0, 8)}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Error al descargar el video";
      onError(message);
    }
  };

  return (
    <div className="video-list-container">
      {videos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🎥</div>
          <h3>No hay videos</h3>
          <p>
            Sube un video en la sección superior para comenzar el procesamiento
          </p>
        </div>
      ) : (
        <>
          {processingVideos.length > 0 && (
            <section className="video-section">
              <h3 className="section-title">
                En Procesamiento ({processingVideos.length})
              </h3>
              <div className="video-grid">
                {processingVideos.map((video) => (
                  <VideoCard
                    key={video.id}
                    video={video}
                    onRefresh={() => onRefresh(video.id)}
                    onDownload={handleDownload}
                  />
                ))}
              </div>
            </section>
          )}

          {completedVideos.length > 0 && (
            <section className="video-section">
              <h3 className="section-title">
                Completados ({completedVideos.length})
              </h3>
              <div className="video-grid">
                {completedVideos.map((video) => (
                  <VideoCard
                    key={video.id}
                    video={video}
                    onRefresh={() => onRefresh(video.id)}
                    onDownload={handleDownload}
                  />
                ))}
              </div>
            </section>
          )}

          {failedVideos.length > 0 && (
            <section className="video-section">
              <h3 className="section-title">
                Con Error ({failedVideos.length})
              </h3>
              <div className="video-grid">
                {failedVideos.map((video) => (
                  <VideoCard
                    key={video.id}
                    video={video}
                    onRefresh={() => onRefresh(video.id)}
                    onDownload={handleDownload}
                  />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
};

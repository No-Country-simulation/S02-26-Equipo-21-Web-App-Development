import React, { useEffect, useState } from "react";
import { Video } from "../types";
import "./VideoCard.css";

interface VideoCardProps {
  video: Video;
  onRefresh: () => void;
  onDownload: (id: string) => void;
}

export const VideoCard: React.FC<VideoCardProps> = ({
  video,
  onRefresh,
  onDownload,
}) => {
  const [refreshInterval, setRefreshInterval] = useState<number | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    // Auto-refresh pending/processing videos every 3 seconds
    if (video.status === "Pending" || video.status === "Processing") {
      const interval = setInterval(() => {
        onRefresh();
      }, 3000);
      setRefreshInterval(interval);
    }

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, [video.status, onRefresh]);

  const getStatusColor = (status: Video["status"]) => {
    switch (status) {
      case "Completed":
        return "success";
      case "Processing":
        return "warning";
      case "Failed":
        return "error";
      case "Pending":
      default:
        return "pending";
    }
  };

  const getStatusIcon = (status: Video["status"]) => {
    switch (status) {
      case "Completed":
        return "✓";
      case "Processing":
        return "⟳";
      case "Failed":
        return "✕";
      case "Pending":
      default:
        return "⧖";
    }
  };

  const getStatusLabel = (status: Video["status"]) => {
    switch (status) {
      case "Completed":
        return "Completado";
      case "Processing":
        return "Procesando";
      case "Failed":
        return "Error";
      case "Pending":
      default:
        return "Pendiente";
    }
  };

  const handleDownload = async () => {
    if (video.status !== "Completed") return;

    try {
      setIsDownloading(true);
      await onDownload(video.id);
    } finally {
      setIsDownloading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("es-ES");
  };

  return (
    <div className={`video-card status-${getStatusColor(video.status)}`}>
      <div className="card-header">
        <div className="status-badge">
          <span className="status-icon">{getStatusIcon(video.status)}</span>
          <span className="status-label">{getStatusLabel(video.status)}</span>
        </div>
        <span className="video-id">{video.id.substring(0, 8)}...</span>
      </div>

      <div className="card-body">
        <div className="file-info">
          <p className="file-name" title={video.fileName}>
            {video.fileName.length > 40
              ? video.fileName.substring(0, 37) + "..."
              : video.fileName}
          </p>
          <p className="created-date">Creado: {formatDate(video.createdAt)}</p>
        </div>

        {video.completedAt && (
          <p className="completed-date">
            Completado: {formatDate(video.completedAt)}
          </p>
        )}

        {video.errorMessage && (
          <div className="error-message">
            <strong>Error:</strong> {video.errorMessage}
          </div>
        )}

        {video.status === "Processing" && (
          <div className="processing-indicator">
            <div className="spinner" />
            <span>Procesando...</span>
          </div>
        )}
      </div>

      <div className="card-footer">
        {video.status === "Completed" && (
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="btn-download"
            title="Descargar video procesado"
          >
            {isDownloading ? "Descargando..." : "⬇ Descargar"}
          </button>
        )}

        <button
          onClick={onRefresh}
          className="btn-refresh"
          title="Actualizar estado"
        >
          🔄
        </button>
      </div>
    </div>
  );
};

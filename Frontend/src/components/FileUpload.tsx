import React, { useRef, useState } from "react";
import { videoApi } from "../services/api";
import "./FileUpload.css";

interface FileUploadProps {
  onUploadSuccess: (videoId: string) => void;
  onError: (message: string) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onError,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const allowedExtensions = [".mp4", ".mov", ".avi", ".mkv"];
  const maxFileSize = 150 * 1024 * 1024; // 150 MB

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      return;
    }

    // Validate file type
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    if (!allowedExtensions.includes(ext)) {
      onError(`Extensión no permitida. Use: ${allowedExtensions.join(", ")}`);
      setSelectedFile(null);
      return;
    }

    // Validate file size
    if (file.size > maxFileSize) {
      onError("El archivo excede el límite de 150 MB");
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      onError("Por favor seleccione un archivo");
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress(0);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) clearInterval(progressInterval);
          return prev + Math.random() * 30;
        });
      }, 500);

      const videoId = await videoApi.uploadVideo(selectedFile);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        onUploadSuccess(videoId);
        setSelectedFile(null);
        setUploadProgress(0);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      }, 500);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Error al subir el archivo";
      onError(message);
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div className="upload-box">
        <div className="upload-icon">🎬</div>
        <h2>Sube tu Video</h2>
        <p className="upload-info">
          Formatos soportados: MP4, MOV, AVI, MKV
          <br />
          Tamaño máximo: 150 MB
        </p>

        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept=".mp4,.mov,.avi,.mkv,video/*"
          className="file-input"
          disabled={isUploading}
        />

        {selectedFile && (
          <div className="selected-file">
            <span className="file-icon">📄</span>
            <div className="file-info">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        )}

        {isUploading && (
          <div className="progress-bar-container">
            <div
              className="progress-bar"
              style={{ width: `${uploadProgress}%` }}
            />
            <p className="progress-text">{Math.round(uploadProgress)}%</p>
          </div>
        )}

        <div className="button-group">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="btn btn-secondary"
          >
            {selectedFile ? "Cambiar Archivo" : "Seleccionar Archivo"}
          </button>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="btn btn-primary"
          >
            {isUploading ? "Subiendo..." : "Subir Video"}
          </button>
        </div>
      </div>
    </div>
  );
};

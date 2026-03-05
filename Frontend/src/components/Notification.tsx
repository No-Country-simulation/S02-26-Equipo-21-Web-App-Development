import React, { useEffect } from "react";
import { NotificationState } from "../types";
import "./Notification.css";

interface NotificationProps extends NotificationState {
  onClose?: () => void;
}

export const Notification: React.FC<NotificationProps> = ({
  type,
  message,
  onClose,
}) => {
  useEffect(() => {
    if (!message) return;

    const timer = setTimeout(() => {
      onClose?.();
    }, 5000);

    return () => clearTimeout(timer);
  }, [message, onClose]);

  if (!message) return null;

  return (
    <div className={`notification notification-${type}`}>
      <div className="notification-content">
        <span className="notification-icon">
          {type === "success" && "✓"}
          {type === "error" && "✕"}
          {type === "info" && "ℹ"}
          {type === "warning" && "⚠"}
        </span>
        <p className="notification-message">{message}</p>
      </div>
      <button
        onClick={onClose}
        className="notification-close"
        aria-label="Cerrar notificación"
      >
        ✕
      </button>
    </div>
  );
};

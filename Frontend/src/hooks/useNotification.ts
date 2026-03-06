import { useCallback } from 'react';
import { NotificationState } from '../types';

let notificationId = 0;

export const useNotification = (
  onNotify: (notification: NotificationState) => void
) => {
  const notify = useCallback(
    (
      message: string,
      type: 'success' | 'error' | 'info' | 'warning' = 'info',
      duration = 5000
    ) => {
      const id = `notification-${notificationId++}`;
      const notification: NotificationState = { id, type, message };

      onNotify(notification);

      if (duration > 0) {
        setTimeout(() => {
          onNotify({ ...notification, message: '' });
        }, duration);
      }

      return id;
    },
    [onNotify]
  );

  return { notify };
};

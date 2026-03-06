export type VideoStatus = 'Pending' | 'Processing' | 'Completed' | 'Failed';

export interface Video {
  id: string;
  fileName: string;
  status: VideoStatus;
  createdAt: string;
  completedAt?: string;
  errorMessage?: string;
  progress?: number;
}

export interface NotificationState {
  id?: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

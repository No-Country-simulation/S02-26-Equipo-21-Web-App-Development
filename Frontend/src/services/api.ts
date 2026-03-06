import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5273/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});


export interface VideoResponse {
  id: string;
  fileName: string;
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed';
  createdAt: string;
  completedAt?: string;
  errorMessage?: string;
}

export interface CreateVideoRequest {
  file: File;
  params?: Record<string, any>;
}

export const videoApi = {
  /**
   * Upload a video file for processing
   */
  uploadVideo: async (file: File, params?: Record<string, any>): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (params) {
      formData.append('params', JSON.stringify(params));
    }

    const response = await apiClient.post<{ id: string }>('/videos', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.id;
  },

  /**
   * Get video details by ID
   */
  getVideoById: async (id: string): Promise<VideoResponse> => {
    const response = await apiClient.get<VideoResponse>(`/videos/${id}`);
    return response.data;
  },

  /**
   * Get all pending videos
   */
  getPendingVideos: async (): Promise<VideoResponse[]> => {
    const response = await apiClient.get<VideoResponse[]>('/videos/pending');
    return response.data;
  },

  /**
   * Download processed video
   */
  downloadVideo: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/videos/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default apiClient;

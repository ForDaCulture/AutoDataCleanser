import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import { getJWT } from './supabaseClient';
import type { ProfileResult, CleanResult, AuditLog, ApiFeatures, ApiError, UploadResult } from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UploadResponse {
  success: boolean;
  session_id: string;
  preview: any[];
  columns: string[];
  rows: number;
}

export const fetchWithAuth = async <T>(config: AxiosRequestConfig & { url: string }): Promise<T> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No token found');

  const response = await apiClient.request<T>({
    ...config,
    headers: {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const uploadFile = async (file: File, onProgress?: (progress: number) => void): Promise<UploadResult> => {
  const token = await getJWT();
  if (!token) {
    throw new Error('No authentication token available');
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post<UploadResult>('/upload', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress?.(progress);
        }
      },
    } as AxiosRequestConfig);

    return response.data;
  } catch (error: any) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      throw new Error(error.response.data.detail || 'Upload failed');
    } else if (error.request) {
      // The request was made but no response was received
      throw new Error('No response from server');
    } else {
      // Something happened in setting up the request that triggered an Error
      throw new Error(error.message || 'Upload failed');
    }
  }
};

export interface ProfileResponse {
  success: boolean;
  profile: Array<{
    column: string;
    type: string;
    missing_pct: number;
    unique_count: number;
    min?: number;
    max?: number;
    mean?: number;
    std?: number;
    min_length?: number;
    max_length?: number;
    avg_length?: number;
  }>;
  preview: any[];
  rows: number;
  columns: string[];
}

export const getProfile = async (sessionId: string): Promise<ProfileResult> => {
  return fetchWithAuth<ProfileResult>({ url: `/profile/${sessionId}` });
};

export const cleanData = async (sessionId: string, options: any): Promise<CleanResult> => {
  return fetchWithAuth<CleanResult>({
    url: '/clean',
    method: 'POST',
    data: { session_id: sessionId, ...options },
  });
};

export const getAudit = async (sessionId: string): Promise<{ logs: AuditLog[] }> => {
  return fetchWithAuth<{ logs: AuditLog[] }>({ url: `/audit/${sessionId}` });
};

export const downloadFile = async (sessionId: string): Promise<Blob> => {
  const token = await getJWT();
  if (!token) {
    throw new Error('No authentication token available');
  }

  const response = await apiClient.get<Blob>(`/download/${sessionId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    responseType: 'blob',
  });

  return response.data;
}; 
import apiClient from './api';
import type { ImportRecord, ImportPreview, ImportConfirmResponse } from '@/types';

export const importsService = {
  async uploadFile(file: File): Promise<ImportRecord> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<ImportRecord>('/imports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getPreview(importId: number): Promise<ImportPreview> {
    const response = await apiClient.get<ImportPreview>(`/imports/${importId}/preview`);
    return response.data;
  },

  async confirmImport(importId: number, categoryMapping?: Record<number, number>): Promise<ImportConfirmResponse> {
    const response = await apiClient.post<ImportConfirmResponse>(`/imports/${importId}/confirm`, {
      import_id: importId,
      category_mapping: categoryMapping,
    });
    return response.data;
  },

  async getHistory(skip = 0, limit = 20): Promise<ImportRecord[]> {
    const response = await apiClient.get<ImportRecord[]>('/imports/history', {
      params: { skip, limit },
    });
    return response.data;
  },

  async listFiles(skip = 0, limit = 20): Promise<ImportRecord[]> {
    const response = await apiClient.get<ImportRecord[]>('/files/', {
      params: { skip, limit },
    });
    return response.data;
  },

  async downloadFile(fileId: number): Promise<Blob> {
    const response = await apiClient.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async deleteFile(fileId: number): Promise<void> {
    await apiClient.delete(`/files/${fileId}`);
  },
};

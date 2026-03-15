import apiClient from './api';
import type { DeletedItem, RecycleBinStats } from '@/types';

export const recycleBinService = {
  async getAll(itemType?: string): Promise<DeletedItem[]> {
    const response = await apiClient.get<DeletedItem[]>('/recycle-bin/', { 
      params: itemType ? { item_type: itemType } : {} 
    });
    return response.data;
  },

  async getStats(): Promise<RecycleBinStats> {
    const response = await apiClient.get<RecycleBinStats>('/recycle-bin/stats');
    return response.data;
  },

  async restoreTransaction(id: number): Promise<void> {
    await apiClient.post(`/recycle-bin/transactions/${id}/restore`);
  },

  async restoreCategory(id: number): Promise<void> {
    await apiClient.post(`/recycle-bin/categories/${id}/restore`);
  },

  async restoreTag(id: number): Promise<void> {
    await apiClient.post(`/recycle-bin/tags/${id}/restore`);
  },

  async permanentlyDeleteTransaction(id: number): Promise<void> {
    await apiClient.delete(`/recycle-bin/transactions/${id}/permanent`);
  },

  async permanentlyDeleteCategory(id: number): Promise<void> {
    await apiClient.delete(`/recycle-bin/categories/${id}/permanent`);
  },

  async permanentlyDeleteTag(id: number): Promise<void> {
    await apiClient.delete(`/recycle-bin/tags/${id}/permanent`);
  },

  async empty(days: number = 30): Promise<void> {
    await apiClient.delete('/recycle-bin/empty', { params: { days } });
  },

  async emptyAll(): Promise<void> {
    await apiClient.delete('/recycle-bin/empty-all');
  },
};

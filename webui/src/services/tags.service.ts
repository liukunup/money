import apiClient from './api';
import type { Tag, TagCreate, TagUpdate } from '@/types';

export const tagsService = {
  async getAll(type?: string): Promise<Tag[]> {
    const params = type ? { type } : {};
    const response = await apiClient.get<Tag[]>('/tags/', { params });
    return response.data;
  },

  async getById(id: number): Promise<Tag> {
    const response = await apiClient.get<Tag>(`/tags/${id}`);
    return response.data;
  },

  async create(data: TagCreate): Promise<Tag> {
    const response = await apiClient.post<Tag>('/tags/', data);
    return response.data;
  },

  async update(id: number, data: TagUpdate): Promise<Tag> {
    const response = await apiClient.put<Tag>(`/tags/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/tags/${id}`);
  },

  async restore(id: number): Promise<Tag> {
    const response = await apiClient.post<Tag>(`/tags/${id}/restore`);
    return response.data;
  },

  async permanentlyDelete(id: number): Promise<void> {
    await apiClient.delete(`/tags/${id}/permanent`);
  },
};

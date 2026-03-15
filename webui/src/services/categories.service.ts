import apiClient from './api';
import type { Category, CategoryCreate } from '@/types';

export const categoriesService = {
  async getAll(type?: 'income' | 'expense'): Promise<Category[]> {
    const response = await apiClient.get<Category[]>('/categories/', {
      params: type ? { type } : undefined,
    });
    return response.data;
  },

  async getById(id: number): Promise<Category> {
    const response = await apiClient.get<Category>(`/categories/${id}`);
    return response.data;
  },

  async create(data: CategoryCreate): Promise<Category> {
    const response = await apiClient.post<Category>('/categories/', data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/categories/${id}`);
  },
};

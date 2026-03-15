import apiClient from './api';
import type { Transaction, TransactionCreate, TransactionUpdate, TransactionFilters } from '@/types';

export const transactionsService = {
  async getAll(filters?: TransactionFilters): Promise<Transaction[]> {
    const response = await apiClient.get<Transaction[]>('/transactions/', { params: filters || {} });
    return response.data;
  },

  async getById(id: number): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  async create(data: TransactionCreate): Promise<Transaction> {
    const response = await apiClient.post<Transaction>('/transactions/', data);
    return response.data;
  },

  async update(id: number, data: TransactionUpdate): Promise<Transaction> {
    const response = await apiClient.put<Transaction>(`/transactions/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/transactions/${id}`);
  },
};

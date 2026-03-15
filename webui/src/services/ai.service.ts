import apiClient from './api';
import type { 
  AIProvider, 
  AIProviderCreate, 
  AIProviderUpdate,
  AIClassificationResult,
  AISuggestionsResponse,
  AISettings 
} from '@/types/models';

export const aiService = {
  // Provider Management
  async getProviders(includeInactive = false) {
    const response = await apiClient.get<AIProvider[]>('/ai/providers', {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  },

  async getSupportedProviders() {
    const response = await apiClient.get('/ai/providers/supported');
    return response.data;
  },

  async createProvider(provider: AIProviderCreate) {
    const response = await apiClient.post<AIProvider>('/ai/providers', provider);
    return response.data;
  },

  async getProvider(id: number) {
    const response = await apiClient.get<AIProvider>(`/ai/providers/${id}`);
    return response.data;
  },

  async updateProvider(id: number, provider: AIProviderUpdate) {
    const response = await apiClient.put<AIProvider>(`/ai/providers/${id}`, provider);
    return response.data;
  },

  async deleteProvider(id: number) {
    await apiClient.delete(`/ai/providers/${id}`);
  },

  async toggleProvider(id: number) {
    const response = await apiClient.post<AIProvider>(`/ai/providers/${id}/toggle`);
    return response.data;
  },

  // Classification
  async classifyTransaction(
    amount: number, 
    transactionType: 'income' | 'expense', 
    note: string
  ) {
    const response = await apiClient.post<AIClassificationResult>('/ai/classify', null, {
      params: {
        amount,
        transaction_type: transactionType,
        note
      }
    });
    return response.data;
  },

  async getSuggestions(note: string, limit = 3) {
    const response = await apiClient.post<AISuggestionsResponse>('/ai/suggestions', null, {
      params: { note, limit }
    });
    return response.data;
  },

  // Settings
  async getSettings() {
    const response = await apiClient.get<AISettings>('/ai/settings');
    return response.data;
  }
};

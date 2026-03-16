import apiClient from './api';
import type { PredictionResponse, CurrentMonthActual, PredictionWithActual } from '@/types';

export const predictionsService = {
  async getPrediction(): Promise<PredictionResponse> {
    const response = await apiClient.get<PredictionResponse>('/predictions/predict');
    return response.data;
  },

  async getCurrentMonthActual(): Promise<CurrentMonthActual> {
    const response = await apiClient.get<CurrentMonthActual>('/predictions/current-month');
    return response.data;
  },

  async getComparison(): Promise<PredictionWithActual> {
    const response = await apiClient.get<PredictionWithActual>('/predictions/comparison');
    return response.data;
  },
};

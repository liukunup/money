import apiClient from './api';
import type { TextParsedTransaction, TextParseRequest } from '@/types';

export const textParseService = {
  async parseText(text: string): Promise<TextParsedTransaction> {
    const response = await apiClient.post<TextParsedTransaction>('/text-parse/parse', { text } as TextParseRequest);
    return response.data;
  },
};

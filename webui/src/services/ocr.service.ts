import apiClient from './api';
import type { TextParsedTransaction } from '@/types';

// OCR Result type
export interface OCRResult {
  success: boolean;
  message?: string;
  amount: string | null;
  date: string | null;
  merchant: string | null;
  category: string | null;
  confidence: number;
  type: 'income' | 'expense';
  note: string | null;
  raw_text?: string;
  provider?: string;
}

// OCR Provider info
export interface OCRProvider {
  id: string;
  name: string;
  description: string;
  free: boolean;
}

// OCR Health info
export interface OCRHealth {
  status: string;
  providers: {
    tesseract: boolean;
    regex: boolean;
  };
}

// OCR Providers response
export interface OCRProvidersResponse {
  providers: OCRProvider[];
  tesseract_available: boolean;
}

export const ocrService = {
  /**
   * Upload receipt/screenshot image for OCR processing
   */
  async parseImage(
    file: File,
    provider: string = 'auto'
  ): Promise<OCRResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider', provider);
    
    const response = await apiClient.post<OCRResult>('/ocr/parse-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: { provider },
    });
    
    return response.data;
  },
  
  /**
   * Parse text directly (for testing or manual input)
   */
  async parseText(text: string): Promise<OCRResult> {
    const response = await apiClient.post<OCRResult>('/ocr/parse-text', { text });
    return response.data;
  },
  
  /**
   * Get available OCR providers
   */
  async getProviders(): Promise<OCRProvidersResponse> {
    const response = await apiClient.get<OCRProvidersResponse>('/ocr/providers');
    return response.data;
  },
  
  /**
   * Check OCR service health
   */
  async healthCheck(): Promise<OCRHealth> {
    const response = await apiClient.get<OCRHealth>('/ocr/health');
    return response.data;
  },
};

// Helper to convert OCR result to TextParsedTransaction format
export function ocrResultToTextParsed(result: OCRResult): TextParsedTransaction {
  return {
    amount: result.amount,
    date: result.date,
    category: result.category,
    merchant: result.merchant,
    note: result.note || result.merchant || null,
    type: result.type || 'expense',
    confidence: result.confidence,
    format_type: result.provider || 'ocr',
  };
}

// API Types

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

// Text Parse Types
export interface TextParsedTransaction {
  amount: string | null;
  date: string | null;
  category: string | null;
  merchant: string | null;
  note: string | null;
  type: 'income' | 'expense';
  confidence: number;
  format_type: string;
}

export interface TextParseRequest {
  text: string;
}

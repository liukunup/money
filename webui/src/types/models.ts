// Model Types

export interface User {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  type: 'income' | 'expense';
  icon?: string;
  created_at: string;
}

export interface Transaction {
  id: number;
  amount: string;
  type: 'income' | 'expense';
  category_id: number;
  date: string;
  note?: string;
  created_at: string;
}

export interface TransactionFilters {
  type?: 'income' | 'expense';
  category_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface TransactionCreate {
  amount: number;
  type: 'income' | 'expense';
  category_id: number;
  date: string;
  note?: string;
}

export interface TransactionUpdate {
  amount?: number;
  type?: 'income' | 'expense';
  category_id?: number;
  date?: string;
  note?: string;
}

export interface CategoryCreate {
  name: string;
  type: 'income' | 'expense';
  icon?: string;
}

export interface MonthlyHistory {
  year: number;
  month: number;
  total: number;
}

export interface CategoryPrediction {
  category_id: number;
  category_name: string;
  category_icon?: string;
  predicted_amount: number;
  ratio: number;
  confidence_low: number;
  confidence_high: number;
}

export interface PredictionResponse {
  predicted_total: number;
  confidence_low: number;
  confidence_high: number;
  based_on_months: number;
  monthly_history: MonthlyHistory[];
  category_predictions: CategoryPrediction[];
}

export interface CurrentMonthActual {
  actual_total: number;
  month: number;
  year: number;
  day_of_month: number;
  days_in_month: number;
}

export interface PredictionWithActual {
  prediction: PredictionResponse;
  current_month: CurrentMonthActual;
  projected_vs_actual: number;
}

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

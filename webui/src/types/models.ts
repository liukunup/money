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
  tag_ids?: number[];
  anomaly_info?: {
    anomaly_level?: 'warning' | 'anomaly' | 'alert' | null;
    category_monthly_average?: string | null;
    anomaly_reason?: string | null;
  };
}

export interface Tag {
  id: number;
  name: string;
  type?: 'general' | 'expense' | 'income';
  color?: string;
  icon?: string;
  description?: string;
  created_at: string;
}

export interface TimePeriod {
  id: number;
  name: string;
  type?: 'custom' | 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  color?: string;
  icon?: string;
  description?: string;
  created_at: string;
}

export interface DeletedItem {
  id: number;
  type: 'transaction' | 'category' | 'tag';
  item_id: number;
  item_type: string;
  name: string;
  deleted_at?: string;
  deleted_by?: number;
}

export interface RecycleBinStats {
  total_transactions: number;
  total_categories: number;
  total_tags: number;
}

export interface TransactionFilters {
  type?: 'income' | 'expense';
  category_id?: number;
  tag_id?: number;
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
  tag_ids?: number[];
}

export interface TransactionUpdate {
  amount?: number;
  type?: 'income' | 'expense';
  category_id?: number;
  date?: string;
  note?: string;
  tag_ids?: number[];
}

export interface CategoryCreate {
  name: string;
  type: 'income' | 'expense';
  icon?: string;
}

export interface TagCreate {
  name: string;
  type?: 'general' | 'expense' | 'income';
  color?: string;
  icon?: string;
  description?: string;
}

export interface TagUpdate {
  name?: string;
  type?: 'general' | 'expense' | 'income';
  color?: string;
  icon?: string;
  description?: string;
}

export interface TimePeriodCreate {
  name: string;
  type?: 'custom' | 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  color?: string;
  icon?: string;
  description?: string;
}

// Budget Types
export interface Budget {
  id: number;
  name: string;
  category_id?: number;
  amount: string;
  period_type: 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  end_date?: string;
  is_active: number;
  created_at: string;
  updated_at?: string;
}

export interface BudgetWithUsage extends Budget {
  spent: string;
  remaining: string;
  percent_used: number;
  category_name?: string;
  category_icon?: string;
}

export interface BudgetCreate {
  name: string;
  category_id?: number;
  amount: number;
  period_type: 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  end_date?: string;
}

export interface BudgetUpdate {
  name?: string;
  category_id?: number;
  amount?: number;
  period_type?: 'weekly' | 'monthly' | 'yearly';
  start_date?: string;
  end_date?: string;
  is_active?: number;
}

// Budget Alert Types
export interface BudgetAlert {
  id: number;
  budget_id: number;
  threshold_percent: number;
  status: 'pending' | 'triggered' | 'resolved';
  triggered_at: string;
  resolved_at?: string;
}

// Analytics Types
export interface BudgetUsage {
  budget_id: number;
  budget_name: string;
  period_type: string;
  start_date: string;
  end_date: string;
  amount: string;
  spent: string;
  remaining: string;
  percent_used: number;
  is_over_budget: boolean;
  alerts_triggered: string[];
}

export interface BudgetSummary {
  total_budgets: number;
  active_budgets: number;
  total_budget_amount: string;
  total_spent: string;
  total_remaining: string;
  budgets: BudgetWithUsage[];
}

// Cash Flow for Sankey
export interface CashFlowNode {
  name: string;
}

export interface CashFlowLink {
  source: string;
  target: string;
  value: number;
}

export interface CashFlowData {
  nodes: CashFlowNode[];
  links: CashFlowLink[];
}

// Heatmap Data
export interface HeatmapData {
  data: number[][];
  period: 'week' | 'month' | 'year';
}

// AI Provider Types
export interface AIProvider {
  id: number;
  name: string;
  provider_type: string;
  base_url: string;
  api_key?: string;
  models?: string[];
  is_active: boolean;
  priority: number;
  created_at: string;
  updated_at?: string;
}

export interface AIProviderCreate {
  name: string;
  provider_type: string;
  base_url: string;
  api_key?: string;
  models?: string[];
  is_active?: boolean;
  priority?: number;
}

export interface AIProviderUpdate {
  name?: string;
  provider_type?: string;
  base_url?: string;
  api_key?: string;
  models?: string[];
  is_active?: boolean;
  priority?: number;
}

export interface AISupportedProvider {
  name: string;
  default_url: string;
  default_models: string[];
}

export interface AIClassificationResult {
  category_id: number;
  confidence: number;
  reason: string;
  category_name?: string;
  is_keyword_fallback?: boolean;
}

export interface AISuggestion {
  category_id: number;
  category_name: string;
  category_icon?: string;
  reason: string;
}

export interface AISuggestionsResponse {
  suggestions: AISuggestion[];
  note: string;
}

export interface AISettings {
  ai_enabled: boolean;
  active_provider_count: number;
  total_provider_count: number;
}

// Import Types
export interface ImportRecord {
  id: number;
  file_name: string;
  file_type: string;
  file_path: string;
  file_hash: string;
  import_count: number;
  status: 'pending' | 'parsed' | 'confirmed' | 'failed';
  error_message?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface ParsedTransaction {
  amount: string | number;
  type: 'income' | 'expense';
  date: string;
  note: string;
  category_id?: number;
  category_name?: string;
}

export interface ImportPreview {
  import_id: number;
  file_name: string;
  total_count: number;
  income_count: number;
  expense_count: number;
  transactions: ParsedTransaction[];
}

export interface ImportConfirmResponse {
  import_id: number;
  created_count: number;
  import_record: ImportRecord;
}

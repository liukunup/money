import axios from 'axios'
import type { BudgetWithUsage, BudgetCreate, BudgetUpdate, BudgetSummary, BudgetAlert, CashFlowData, HeatmapData } from '@/types/models'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const budgetsService = {
  // Get all budgets
  async getBudgets(params?: { period_type?: string; category_id?: number; active_only?: boolean }) {
    const response = await api.get<BudgetWithUsage[]>('/budgets/', { params })
    return response.data
  },

  // Get single budget
  async getBudget(id: number) {
    const response = await api.get<BudgetWithUsage>(`/budgets/${id}`)
    return response.data
  },

  // Create budget
  async createBudget(budget: BudgetCreate) {
    const response = await api.post<BudgetWithUsage>('/budgets/', budget)
    return response.data
  },

  // Update budget
  async updateBudget(id: number, budget: BudgetUpdate) {
    const response = await api.put<BudgetWithUsage>(`/budgets/${id}`, budget)
    return response.data
  },

  // Delete budget
  async deleteBudget(id: number) {
    await api.delete(`/budgets/${id}`)
  },

  // Get budget usage analytics
  async getBudgetUsage(period_type?: string) {
    const response = await api.get('/budgets/analytics/usage', { params: { period_type } })
    return response.data
  },

  // Get budget summary
  async getBudgetSummary() {
    const response = await api.get<BudgetSummary>('/budgets/analytics/summary')
    return response.data
  },

  // Get alerts
  async getAlerts(params?: { budget_id?: number; status?: string }) {
    const response = await api.get<BudgetAlert[]>('/budgets/alerts', { params })
    return response.data
  },

  // Get cash flow data (for Sankey chart)
  async getCashFlow(params?: { start_date?: string; end_date?: string }) {
    const response = await api.get<CashFlowData>('/budgets/analytics/cash-flow', { params })
    return response.data
  },

  // Get heatmap data
  async getHeatmap(period: 'week' | 'month' | 'year' = 'month') {
    const response = await api.get<HeatmapData>('/budgets/analytics/heatmap', { params: { period } })
    return response.data
  },
}

export default budgetsService
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import budgetsService from '@/services/budgets.service'
import type { BudgetWithUsage, BudgetCreate, BudgetUpdate, BudgetSummary, BudgetAlert } from '@/types/models'

export const useBudgetsStore = defineStore('budgets', () => {
  const budgets = ref<BudgetWithUsage[]>([])
  const summary = ref<BudgetSummary | null>(null)
  const alerts = ref<BudgetAlert[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeBudgets = computed(() => budgets.value.filter(b => b.is_active === 1))
  
  const totalBudgetAmount = computed(() => 
    activeBudgets.value.reduce((sum, b) => sum + parseFloat(b.amount), 0)
  )
  
  const totalSpent = computed(() => 
    activeBudgets.value.reduce((sum, b) => sum + parseFloat(b.spent), 0)
  )

  // Actions
  async function fetchBudgets(params?: { period_type?: string; category_id?: number }) {
    loading.value = true
    error.value = null
    try {
      budgets.value = await budgetsService.getBudgets({ ...params, active_only: true })
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch budgets'
    } finally {
      loading.value = false
    }
  }

  async function fetchSummary() {
    loading.value = true
    error.value = null
    try {
      summary.value = await budgetsService.getBudgetSummary()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch budget summary'
    } finally {
      loading.value = false
    }
  }

  async function fetchAlerts(budgetId?: number) {
    try {
      alerts.value = await budgetsService.getAlerts({ budget_id: budgetId })
    } catch (e: any) {
      console.error('Failed to fetch alerts:', e)
    }
  }

  async function createBudget(budget: BudgetCreate) {
    loading.value = true
    error.value = null
    try {
      const newBudget = await budgetsService.createBudget(budget)
      budgets.value.unshift(newBudget)
      return newBudget
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create budget'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateBudget(id: number, budget: BudgetUpdate) {
    loading.value = true
    error.value = null
    try {
      const updated = await budgetsService.updateBudget(id, budget)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to update budget'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteBudget(id: number) {
    loading.value = true
    error.value = null
    try {
      await budgetsService.deleteBudget(id)
      budgets.value = budgets.value.filter(b => b.id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete budget'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    budgets,
    summary,
    alerts,
    loading,
    error,
    activeBudgets,
    totalBudgetAmount,
    totalSpent,
    fetchBudgets,
    fetchSummary,
    fetchAlerts,
    createBudget,
    updateBudget,
    deleteBudget,
  }
})
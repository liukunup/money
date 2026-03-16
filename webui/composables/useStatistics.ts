import { computed, type ComputedRef } from 'vue'
import { useTransactionsStore } from '@/stores/transactions'
import type { Transaction } from '@/types/models'

/**
 * Composable for calculating financial statistics
 * Returns computed values for balance, income, expense, and transaction counts
 */
export function useStatistics() {
  const transactionsStore = useTransactionsStore()

  // Filter transactions for current month
  const currentMonthTransactions = computed(() => {
    const now = new Date()
    const currentMonth = now.getMonth()
    const currentYear = now.getFullYear()

    return transactionsStore.transactions.filter((transaction) => {
      const transactionDate = new Date(transaction.date)
      return (
        transactionDate.getMonth() === currentMonth &&
        transactionDate.getFullYear() === currentYear
      )
    })
  })

  // Calculate total income
  const totalIncome: ComputedRef<number> = computed(() => {
    return currentMonthTransactions.value
      .filter((t) => t.type === 'income')
      .reduce((sum, t) => {
        const amount = typeof t.amount === 'string' ? parseFloat(t.amount) : t.amount
        return sum + amount
      }, 0)
  })

  // Calculate total expense
  const totalExpense: ComputedRef<number> = computed(() => {
    return currentMonthTransactions.value
      .filter((t) => t.type === 'expense')
      .reduce((sum, t) => {
        const amount = typeof t.amount === 'string' ? parseFloat(t.amount) : t.amount
        return sum + amount
      }, 0)
  })

  // Calculate balance
  const balance: ComputedRef<number> = computed(() => {
    return totalIncome.value - totalExpense.value
  })

  // Count transactions this month
  const transactionCount: ComputedRef<number> = computed(() => {
    return currentMonthTransactions.value.length
  })

  // Get recent transactions (last 5, all time)
  const recentTransactions: ComputedRef<Transaction[]> = computed(() => {
    return [...transactionsStore.transactions]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 5)
  })

  // Calculate average daily spending this month
  const averageDailyExpense: ComputedRef<number> = computed(() => {
    const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate()
    return totalExpense.value / daysInMonth
  })

  // Calculate largest expense this month
  const largestExpense: ComputedRef<Transaction | null> = computed(() => {
    const expenses = currentMonthTransactions.value.filter((t) => t.type === 'expense')
    if (expenses.length === 0) return null
    return expenses.reduce((max, t) => (t.amount > max.amount ? t : max))
  })

  return {
    totalIncome,
    totalExpense,
    balance,
    transactionCount,
    recentTransactions,
    averageDailyExpense,
    largestExpense,
  }
}

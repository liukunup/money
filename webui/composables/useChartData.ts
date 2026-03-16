import { computed } from 'vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useCategoriesStore } from '@/stores/categories'

/**
 * Composable for preparing chart data
 * Returns formatted data for ECharts visualization
 */
export function useChartData() {
  const transactionsStore = useTransactionsStore()
  const categoriesStore = useCategoriesStore()

  // Group transactions by date for trend chart (last 30 days)
  const trendData = computed(() => {
    const now = new Date()
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

    const filtered = transactionsStore.transactions.filter((t) => {
      const date = new Date(t.date)
      return date >= thirtyDaysAgo
    })

    // Group by date
    const grouped = filtered.reduce(
      (acc, t) => {
        const date = new Date(t.date).toISOString().split('T')[0]
        if (!acc[date]) {
          acc[date] = { income: 0, expense: 0 }
        }
        const amount = typeof t.amount === 'string' ? parseFloat(t.amount) : t.amount
        if (t.type === 'income') {
          acc[date].income += amount
        } else {
          acc[date].expense += amount
        }
        return acc
      },
      {} as Record<string, { income: number; expense: number }>
    )

    // Sort by date
    const sortedDates = Object.keys(grouped).sort()

    return {
      dates: sortedDates,
      income: sortedDates.map((date) => grouped[date].income),
      expense: sortedDates.map((date) => grouped[date].expense),
    }
  })

  // Group expenses by category for pie chart (current month)
  const categoryDistribution = computed(() => {
    const now = new Date()
    const currentMonth = now.getMonth()
    const currentYear = now.getFullYear()

    const currentMonthExpenses = transactionsStore.transactions.filter((t) => {
      const date = new Date(t.date)
      return (
        t.type === 'expense' &&
        date.getMonth() === currentMonth &&
        date.getFullYear() === currentYear
      )
    })

    const grouped = currentMonthExpenses.reduce(
      (acc, t) => {
        const category = categoriesStore.categories.find((c) => c.id === t.category_id)
        const categoryName = category?.name || 'Unknown'
        if (!acc[categoryName]) {
          acc[categoryName] = 0
        }
        const amount = typeof t.amount === 'string' ? parseFloat(t.amount) : t.amount
        acc[categoryName] += amount
        return acc
      },
      {} as Record<string, number>
    )

    return Object.entries(grouped)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
  })

  // Monthly comparison (last 6 months)
  const monthlyComparison = computed(() => {
    const months: Array<{ month: string; income: number; expense: number }> = []
    const now = new Date()

    for (let i = 5; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const monthName = date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })

      const monthTransactions = transactionsStore.transactions.filter((t) => {
        const tDate = new Date(t.date)
        return tDate.getMonth() === date.getMonth() && tDate.getFullYear() === date.getFullYear()
      })

      const income = monthTransactions
        .filter((t) => t.type === 'income')
        .reduce((sum, t) => {
          const amount = typeof t.amount === 'string' ? parseFloat(t.amount) : t.amount
          return sum + amount
        }, 0)
      const expense = monthTransactions
        .filter((t) => t.type === 'expense')
        .reduce((sum, t) => {
          const amount = typeof t.amount === 'string' ? parseFloat(t.amount) : t.amount
          return sum + amount
        }, 0)

      months.push({ month: monthName, income, expense })
    }

    return {
      months: months.map((m) => m.month),
      income: months.map((m) => m.income),
      expense: months.map((m) => m.expense),
    }
  })

  // Get category icon for pie chart
  const getCategoryIcon = (categoryName: string): string => {
    const category = categoriesStore.categories.find((c) => c.name === categoryName)
    return category?.icon || '📊'
  }

  return {
    trendData,
    categoryDistribution,
    monthlyComparison,
    getCategoryIcon,
  }
}

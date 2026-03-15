<template>
  <div class="statistics">
    <!-- Header -->
    <header class="statistics-header">
      <h1 class="statistics-title">Statistics</h1>
      <p class="statistics-subtitle">Your financial insights</p>
    </header>

    <!-- Loading State -->
    <div v-if="transactionsStore.loading || categoriesStore.loading" class="loading-state">
      <Card v-for="i in 2" :key="i" variant="elevated" class="chart-card skeleton">
        <div class="skeleton-content">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line chart"></div>
        </div>
      </Card>
    </div>

    <!-- Charts -->
    <div v-else class="charts-container">
      <!-- Trend Chart -->
      <Card variant="elevated" class="chart-card">
        <LineChart
          :title="`${new Date().toLocaleDateString('en-US', { month: 'long' })} Trend (30 Days)`"
          :x-data="trendData.dates"
          :series="[
            { name: 'Income', data: trendData.income, color: '#34C759' },
            { name: 'Expense', data: trendData.expense, color: '#FF3B30' },
          ]"
        />
      </Card>

      <!-- Category Distribution -->
      <Card v-if="categoryDistribution.length > 0" variant="elevated" class="chart-card">
        <PieChart
          title="Expense Distribution"
          :data="categoryDistribution"
          :show-icon="true"
          :get-icon="getCategoryIcon"
        />
      </Card>

      <!-- Empty State for Categories -->
      <Card v-else variant="elevated" class="chart-card empty-card">
        <div class="empty-state">
          <div class="empty-icon">📊</div>
          <p class="empty-message">No expense data for this month</p>
          <Button variant="tertiary" @click="$router.push('/transactions')">
            Add Transactions
          </Button>
        </div>
      </Card>

      <!-- Monthly Comparison -->
      <Card variant="elevated" class="chart-card">
        <LineChart
          title="Monthly Comparison (6 Months)"
          :x-data="monthlyComparison.months"
          :series="[
            { name: 'Income', data: monthlyComparison.income, color: '#34C759' },
            { name: 'Expense', data: monthlyComparison.expense, color: '#FF3B30' },
          ]"
        />
      </Card>
    </div>

    <!-- Summary Stats -->
    <section v-if="!transactionsStore.loading" class="summary-stats">
      <h2 class="section-title">Summary</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">Total Income (6 Months)</div>
          <div class="stat-value positive">
            {{ formatCurrency(totalSixMonthIncome) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Total Expense (6 Months)</div>
          <div class="stat-value negative">
            {{ formatCurrency(totalSixMonthExpense) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Net Balance</div>
          <div class="stat-value" :class="{ positive: netBalance >= 0, negative: netBalance < 0 }">
            {{ formatCurrency(netBalance) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Total Transactions</div>
          <div class="stat-value">
            {{ totalTransactions }}
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import LineChart from '@/components/charts/LineChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useCategoriesStore } from '@/stores/categories'
import { useChartData } from '@/composables/useChartData'

const transactionsStore = useTransactionsStore()
const categoriesStore = useCategoriesStore()

// Use chart data composable
const { trendData, categoryDistribution, monthlyComparison, getCategoryIcon } = useChartData()

// Calculate summary stats
const totalSixMonthIncome = computed(() => {
  return (monthlyComparison.value.income as number[]).reduce((sum: number, val: number) => sum + val, 0)
})

const totalSixMonthExpense = computed(() => {
  return (monthlyComparison.value.expense as number[]).reduce((sum: number, val: number) => sum + val, 0)
})

const netBalance = computed(() => {
  return totalSixMonthIncome.value - totalSixMonthExpense.value
})

const totalTransactions = computed(() => {
  return transactionsStore.transactions.length
})

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

// Load data on mount
transactionsStore.fetchTransactions()
categoriesStore.fetchCategories()
</script>

<style scoped>
.statistics {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
}

/* Header */
.statistics-header {
  margin-bottom: 32px;
}

.statistics-title {
  font-size: 34px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.statistics-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Loading State */
.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

/* Charts Container */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.chart-card {
  background: var(--color-surface-primary);
  border-radius: var(--radius-xl);
  padding: 20px;
  min-height: 360px;
  display: flex;
  flex-direction: column;
}

/* Skeleton Loading */
.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.skeleton-line {
  background: linear-gradient(
    90deg,
    var(--color-surface-secondary) 25%,
    var(--color-surface-tertiary) 50%,
    var(--color-surface-secondary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

.skeleton-line.title {
  height: 24px;
  width: 40%;
}

.skeleton-line.chart {
  flex: 1;
  width: 100%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Empty Card */
.empty-card {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 16px;
}

.empty-icon {
  font-size: 64px;
}

.empty-message {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Summary Stats */
.summary-stats {
  background: var(--color-surface-primary);
  border-radius: var(--radius-xl);
  padding: 24px;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 20px 0;
  letter-spacing: -0.3px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--color-surface-secondary);
  border-radius: var(--radius-lg);
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  letter-spacing: -0.1px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

.stat-value.positive {
  color: var(--color-success);
}

.stat-value.negative {
  color: var(--color-destructive);
}

/* Responsive Design */
@media (max-width: 768px) {
  .statistics {
    padding: 16px;
  }

  .statistics-title {
    font-size: 28px;
  }

  .statistics-subtitle {
    font-size: 15px;
  }

  .loading-state,
  .charts-container {
    grid-template-columns: 1fr;
  }

  .chart-card {
    min-height: 320px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-value {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .statistics {
    padding: 12px;
  }

  .chart-card {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .summary-stats {
    padding: 16px;
  }
}
</style>

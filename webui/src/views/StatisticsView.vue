<template>
  <div class="statistics">
    <header class="statistics-header">
      <h1 class="statistics-title">{{ t('statistics.title') }}</h1>
      <p class="statistics-subtitle">{{ t('statistics.subtitle') }}</p>
    </header>

    <div v-if="transactionsStore.loading || categoriesStore.loading" class="loading-state">
      <Card v-for="i in 4" :key="i" variant="elevated" class="chart-card skeleton">
        <div class="skeleton-content">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line chart"></div>
        </div>
      </Card>
    </div>

    <div v-else class="charts-container">
      <Card variant="elevated" class="chart-card">
        <LineChart
          :title="trendTitle"
          :x-data="trendData.dates"
          :series="[
            { name: t('transactions.income'), data: trendData.income, color: '#34C759' },
            { name: t('transactions.expense'), data: trendData.expense, color: '#FF3B30' },
          ]"
        />
      </Card>

      <Card v-if="categoryDistribution.length > 0" variant="elevated" class="chart-card">
        <PieChart
          :title="t('statistics.expenseDistribution')"
          :data="categoryDistribution"
          :show-icon="true"
          :get-icon="getCategoryIcon"
        />
      </Card>

      <Card v-else variant="elevated" class="chart-card empty-card">
        <div class="empty-state">
          <div class="empty-icon">📊</div>
          <p class="empty-message">{{ t('statistics.noExpenseData') }}</p>
          <Button variant="tertiary" @click="$router.push('/transactions')">
            {{ t('statistics.addTransactions') }}
          </Button>
        </div>
      </Card>

      <Card variant="elevated" class="chart-card">
        <LineChart
          :title="t('statistics.monthlyComparison')"
          :x-data="monthlyComparison.months"
          :series="[
            { name: t('transactions.income'), data: monthlyComparison.income, color: '#34C759' },
            { name: t('transactions.expense'), data: monthlyComparison.expense, color: '#FF3B30' },
          ]"
        />
      </Card>

      <Card variant="elevated" class="chart-card">
        <SankeyChart
          :title="t('statistics.cashFlow')"
          :nodes="sankeyNodes"
          :links="sankeyLinks"
        />
      </Card>

      <Card variant="elevated" class="chart-card">
        <HeatmapChart
          :title="t('statistics.spendingHabits')"
          :data="heatmapData"
          @period-change="handleHeatmapPeriodChange"
        />
      </Card>
    </div>

    <section v-if="!transactionsStore.loading" class="summary-stats">
      <h2 class="section-title">{{ t('statistics.summary') }}</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">{{ t('statistics.totalIncome') }}</div>
          <div class="stat-value positive">
            {{ formatCurrency(totalSixMonthIncome) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">{{ t('statistics.totalExpense') }}</div>
          <div class="stat-value negative">
            {{ formatCurrency(totalSixMonthExpense) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">{{ t('statistics.netBalance') }}</div>
          <div class="stat-value" :class="{ positive: netBalance >= 0, negative: netBalance < 0 }">
            {{ formatCurrency(netBalance) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">{{ t('statistics.totalTransactions') }}</div>
          <div class="stat-value">
            {{ totalTransactions }}
          </div>
        </div>
      </div>
    </section>

    <section v-if="!transactionsStore.loading" class="anomaly-section">
      <h2 class="section-title">{{ t('anomaly.title') }}</h2>
      <div class="anomaly-stats-grid">
        <div class="anomaly-stat-card warning">
          <div class="anomaly-stat-icon">⚠️</div>
          <div class="anomaly-stat-value">{{ anomalyStats.warning }}</div>
          <div class="anomaly-stat-label">{{ t('anomaly.warning') }}</div>
        </div>
        <div class="anomaly-stat-card anomaly">
          <div class="anomaly-stat-icon">🔴</div>
          <div class="anomaly-stat-value">{{ anomalyStats.anomaly }}</div>
          <div class="anomaly-stat-label">{{ t('anomaly.anomaly') }}</div>
        </div>
        <div class="anomaly-stat-card alert">
          <div class="anomaly-stat-icon">🚨</div>
          <div class="anomaly-stat-value">{{ anomalyStats.alert }}</div>
          <div class="anomaly-stat-label">{{ t('anomaly.alert') }}</div>
        </div>
      </div>
      <Button variant="secondary" @click="$router.push('/anomalies')">
        {{ t('anomaly.viewAll') }}
      </Button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { LineChart, PieChart, SankeyChart, HeatmapChart } from '@/components/charts'
import { useTransactionsStore } from '@/stores/transactions'
import { useCategoriesStore } from '@/stores/categories'
import { useChartData } from '@/composables/useChartData'
import { useAnalyticsData } from '@/composables/useAnalyticsData'

const { t } = useI18n()
const transactionsStore = useTransactionsStore()
const categoriesStore = useCategoriesStore()

const { trendData, categoryDistribution, monthlyComparison, getCategoryIcon } = useChartData()
const { sankeyNodes, sankeyLinks, heatmapData, fetchCashFlow, fetchHeatmap } = useAnalyticsData()

const trendTitle = computed(() => {
  const locale = localStorage.getItem('locale') || 'zh-CN'
  const monthName = new Date().toLocaleDateString(locale === 'en-US' ? 'en-US' : 'zh-CN', { month: 'long' })
  return t('statistics.trendTitle', { month: monthName })
})

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

const anomalyStats = computed(() => {
  return {
    warning: transactionsStore.anomalyStatistics?.warning || 0,
    anomaly: transactionsStore.anomalyStatistics?.anomaly || 0,
    alert: transactionsStore.anomalyStatistics?.alert || 0
  }
})

const formatCurrency = (amount: number): string => {
  const locale = localStorage.getItem('locale') || 'zh-CN'
  return new Intl.NumberFormat(locale === 'en-US' ? 'en-US' : 'zh-CN', {
    style: 'currency',
    currency: locale === 'en-US' ? 'USD' : 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

const handleHeatmapPeriodChange = (period: 'week' | 'month' | 'year') => {
  fetchHeatmap(period)
}

onMounted(() => {
  transactionsStore.fetchTransactions()
  transactionsStore.fetchAnomalies()
  categoriesStore.fetchCategories()
  fetchCashFlow()
  fetchHeatmap('month')
})
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

/* Anomaly Section */
.anomaly-section {
  margin-top: 24px;
  padding: 20px;
  background: var(--color-surface-primary);
  border-radius: 16px;
}

.anomaly-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.anomaly-stat-card {
  text-align: center;
  padding: 16px;
  border-radius: 12px;
}

.anomaly-stat-card.warning {
  background: rgba(255, 149, 0, 0.1);
}

.anomaly-stat-card.anomaly {
  background: rgba(255, 59, 48, 0.1);
}

.anomaly-stat-card.alert {
  background: rgba(175, 82, 222, 0.1);
}

.anomaly-stat-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.anomaly-stat-value {
  font-size: 28px;
  font-weight: 700;
}

.anomaly-stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
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

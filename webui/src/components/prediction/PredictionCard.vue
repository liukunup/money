<template>
  <Card variant="elevated" class="prediction-card">
    <div class="card-header">
      <div class="header-icon">📊</div>
      <div class="header-content">
        <h3 class="card-title">{{ t('prediction.title') }}</h3>
        <p class="card-subtitle">{{ t('prediction.subtitle', { months: 3 }) }}</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="skeleton-line title"></div>
      <div class="skeleton-line value"></div>
      <div class="skeleton-line range"></div>
    </div>

    <div v-else-if="!hasData" class="empty-state">
      <div class="empty-icon">📈</div>
      <p class="empty-message">{{ t('prediction.noData') }}</p>
    </div>

    <div v-else class="prediction-content">
      <div class="main-prediction">
        <div class="prediction-label">{{ t('prediction.nextMonth') }}</div>
        <div class="prediction-value">
          {{ formatCurrency(data.prediction.predicted_total) }}
        </div>
        <div class="confidence-range">
          {{ t('prediction.confidenceRange', {
            low: formatCurrency(data.prediction.confidence_low),
            high: formatCurrency(data.prediction.confidence_high)
          }) }}
        </div>
      </div>

      <div v-if="showComparison && data.current_month" class="comparison">
        <div class="comparison-item">
          <span class="comparison-label">{{ t('prediction.currentMonthActual') }}</span>
          <span class="comparison-value">{{ formatCurrency(data.current_month.actual_total) }}</span>
        </div>
        <div class="comparison-item">
          <span class="comparison-label">{{ t('prediction.progress') }}</span>
          <span 
            class="comparison-value"
            :class="{ 
              'positive': data.projected_vs_actual < 0,
              'negative': data.projected_vs_actual > 0 
            }"
          >
            {{ data.projected_vs_actual > 0 ? '+' : '' }}{{ data.projected_vs_actual.toFixed(1) }}%
          </span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill"
            :class="{ 
              'over': progressPercent > 100,
              'warning': progressPercent > 80 && progressPercent <= 100
            }"
            :style="{ width: `${Math.min(progressPercent, 100)}%` }"
          ></div>
        </div>
      </div>

      <div v-if="data.prediction.category_predictions?.length > 0" class="category-predictions">
        <div class="category-header">{{ t('prediction.categoryBreakdown') }}</div>
        <div class="category-list">
          <div 
            v-for="cat in data.prediction.category_predictions.slice(0, 5)" 
            :key="cat.category_id"
            class="category-item"
          >
            <div class="category-info">
              <span class="category-icon">{{ cat.category_icon || '📁' }}</span>
              <span class="category-name">{{ cat.category_name }}</span>
            </div>
            <div class="category-amount">{{ formatCurrency(cat.predicted_amount) }}</div>
            <div class="category-bar-container">
              <div 
                class="category-bar"
                :style="{ width: `${cat.ratio}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="based-on">
        {{ t('prediction.basedOn', { months: data.prediction.based_on_months }) }}
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import { predictionsService } from '@/services/predictions.service'
import type { PredictionWithActual } from '@/types'

interface Props {
  showComparison?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showComparison: true
})

const { t } = useI18n()

const loading = ref(true)
const hasData = ref(false)
const data = ref<PredictionWithActual | null>(null)

const progressPercent = computed(() => {
  if (!data.value?.prediction?.predicted_total || !data.value?.current_month?.actual_total) {
    return 0
  }
  return (data.value.current_month.actual_total / data.value.prediction.predicted_total) * 100
})

const formatCurrency = (amount: number): string => {
  const locale = localStorage.getItem('locale') || 'zh-CN'
  return new Intl.NumberFormat(locale === 'en-US' ? 'en-US' : 'zh-CN', {
    style: 'currency',
    currency: locale === 'en-US' ? 'USD' : 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

const fetchPrediction = async () => {
  try {
    loading.value = true
    const result = await predictionsService.getComparison()
    data.value = result
    hasData.value = result.prediction.predicted_total > 0
  } catch (error) {
    console.error('Failed to fetch prediction:', error)
    hasData.value = false
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPrediction()
})
</script>

<style scoped>
.prediction-card {
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-surface-secondary) 100%);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.header-icon {
  font-size: 28px;
  line-height: 1;
}

.header-content {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.card-subtitle {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  height: 16px;
  width: 60%;
}

.skeleton-line.value {
  height: 32px;
  width: 80%;
}

.skeleton-line.range {
  height: 14px;
  width: 50%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-6) 0;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-3);
}

.empty-message {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

.prediction-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.main-prediction {
  text-align: center;
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--color-separator);
}

.prediction-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.prediction-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

.confidence-range {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-top: var(--space-1);
}

.comparison {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-surface-secondary);
  border-radius: var(--radius-lg);
}

.comparison-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comparison-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.comparison-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.comparison-value.positive {
  color: var(--color-success);
}

.comparison-value.negative {
  color: var(--color-destructive);
}

.progress-bar {
  height: 8px;
  background: var(--color-surface-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-success);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.progress-fill.warning {
  background: var(--color-warning);
}

.progress-fill.over {
  background: var(--color-destructive);
}

.category-predictions {
  padding-top: var(--space-2);
}

.category-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.category-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--space-2);
  align-items: center;
  padding: var(--space-2);
  background: var(--color-surface-secondary);
  border-radius: var(--radius-md);
}

.category-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 100px;
}

.category-icon {
  font-size: 16px;
}

.category-name {
  font-size: 14px;
  color: var(--color-text-primary);
}

.category-amount {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: right;
}

.category-bar-container {
  grid-column: 1 / -1;
  height: 4px;
  background: var(--color-surface-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.category-bar {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
}

.based-on {
  font-size: 12px;
  color: var(--color-text-tertiary);
  text-align: center;
  padding-top: var(--space-2);
}

@media (max-width: 480px) {
  .prediction-value {
    font-size: 28px;
  }

  .category-info {
    min-width: 80px;
  }

  .category-name {
    font-size: 13px;
  }

  .category-amount {
    font-size: 13px;
  }
}
</style>

<template>
  <div class="budget-progress">
    <div class="progress-header">
      <div class="budget-info">
        <span class="budget-icon">{{ icon }}</span>
        <span class="budget-name">{{ name }}</span>
      </div>
      <span class="period-badge">{{ periodLabel }}</span>
    </div>
    
    <div class="progress-bar-container">
      <div 
        class="progress-bar" 
        :style="{ width: `${Math.min(percentUsed, 100)}%` }"
        :class="progressClass"
      ></div>
      <div class="threshold-markers">
        <div class="marker marker-80" :class="{ exceeded: percentUsed >= 80 }"></div>
        <div class="marker marker-100" :class="{ exceeded: percentUsed >= 100 }"></div>
      </div>
    </div>
    
    <div class="progress-stats">
      <div class="stat">
        <span class="stat-label">Spent</span>
        <span class="stat-value">{{ formatCurrency(spent) }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Budget</span>
        <span class="stat-value">{{ formatCurrency(amount) }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Remaining</span>
        <span class="stat-value" :class="{ negative: remaining < 0 }">
          {{ formatCurrency(remaining) }}
        </span>
      </div>
    </div>
    
    <div v-if="percentUsed >= 80" class="alert-badge" :class="{ critical: percentUsed >= 100 }">
      {{ percentUsed >= 100 ? 'Budget Exceeded!' : 'Approaching Limit' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  name: string
  amount: number
  spent: number
  periodType: 'weekly' | 'monthly' | 'yearly'
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: '💰',
})

const percentUsed = computed(() => {
  if (props.amount === 0) return 0
  return (props.spent / props.amount) * 100
})

const remaining = computed(() => props.amount - props.spent)

const periodLabel = computed(() => {
  const labels: Record<string, string> = {
    weekly: 'Weekly',
    monthly: 'Monthly',
    yearly: 'Yearly',
  }
  return labels[props.periodType] || props.periodType
})

const progressClass = computed(() => {
  if (percentUsed.value >= 100) return 'critical'
  if (percentUsed.value >= 80) return 'warning'
  return 'normal'
})

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}
</script>

<style scoped>
.budget-progress {
  padding: 16px;
  background: var(--color-surface-secondary);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.budget-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.budget-icon {
  font-size: 20px;
}

.budget-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.period-badge {
  font-size: 12px;
  padding: 4px 8px;
  background: var(--color-surface-tertiary);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
}

.progress-bar-container {
  position: relative;
  height: 8px;
  background: var(--color-surface-tertiary);
  border-radius: 4px;
  overflow: visible;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-bar.normal {
  background: var(--color-success);
}

.progress-bar.warning {
  background: var(--color-warning);
}

.progress-bar.critical {
  background: var(--color-destructive);
}

.threshold-markers {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  pointer-events: none;
}

.marker {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 12px;
  background: var(--color-border);
  opacity: 0.5;
}

.marker-80 {
  left: 80%;
}

.marker-100 {
  left: 100%;
}

.marker.exceeded {
  background: var(--color-destructive);
  opacity: 1;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.stat-value.negative {
  color: var(--color-destructive);
}

.alert-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  text-align: center;
  background: var(--color-warning);
  color: #000;
}

.alert-badge.critical {
  background: var(--color-destructive);
  color: #fff;
}
</style>
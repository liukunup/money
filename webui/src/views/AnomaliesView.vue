<template>
  <div class="anomalies-page">
    <div class="page-header">
      <h1>{{ t('anomalies.title') }}</h1>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>

    <div v-else-if="!anomalies.length" class="empty-state">
      <span class="empty-icon">✅</span>
      <p>{{ t('anomalies.noAnomalies') }}</p>
    </div>

    <div v-else class="anomalies-content">
      <Card>
        <div class="summary">
          <div class="stat">
            <span class="stat-value">{{ summary.total }}</span>
            <span class="stat-label">{{ t('anomalies.total') }}</span>
          </div>
          <div class="stat warning">
            <span class="stat-value">{{ summary.warnings }}</span>
            <span class="stat-label">{{ t('anomalies.warnings') }}</span>
          </div>
          <div class="stat danger">
            <span class="stat-value">{{ summary.anomalies }}</span>
            <span class="stat-label">{{ t('anomalies.anomalies') }}</span>
          </div>
        </div>
      </Card>

      <div class="anomalies-list">
        <Card v-for="item in anomalies" :key="item.id">
          <div class="anomaly-item" :class="item.level">
            <div class="anomaly-icon">
              {{ item.level === 'anomaly' ? '⚠️' : '⚡' }}
            </div>
            <div class="anomaly-info">
              <div class="anomaly-amount">
                ¥{{ item.amount.toFixed(2) }}
              </div>
              <div class="anomaly-meta">
                {{ item.category }} • {{ item.date }}
              </div>
              <div class="anomaly-note" v-if="item.note">
                {{ item.note }}
              </div>
            </div>
            <div class="anomaly-badge">
              {{ item.message }}
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'

const { t } = useI18n()

interface Anomaly {
  id: number
  amount: number
  date: string
  note: string
  category: string
  ratio: number
  level: string
  message: string
}

const anomalies = ref<Anomaly[]>([])
const summary = ref({ total: 0, warnings: 0, anomalies: 0 })
const loading = ref(true)

const fetchAnomalies = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/analytics/anomalies', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      anomalies.value = data.transactions || []
      summary.value = data.summary || { total: 0, warnings: 0, anomalies: 0 }
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

onMounted(() => {
  fetchAnomalies()
})
</script>

<style scoped>
.anomalies-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.loading {
  text-align: center;
  padding: 48px;
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: 48px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.summary {
  display: flex;
  justify-content: space-around;
  padding: 16px 0;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  display: block;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.stat.warning .stat-value {
  color: #f59e0b;
}

.stat.danger .stat-value {
  color: #ef4444;
}

.anomalies-list {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.anomaly-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
}

.anomaly-item.warning {
  background: #fef3c7;
}

.anomaly-item.anomaly {
  background: #fee2e2;
}

.anomaly-icon {
  font-size: 24px;
}

.anomaly-info {
  flex: 1;
}

.anomaly-amount {
  font-size: 18px;
  font-weight: 600;
}

.anomaly-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.anomaly-note {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.anomaly-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: var(--color-bg-secondary);
}

.anomaly-item.warning .anomaly-badge {
  background: #f59e0b20;
  color: #d97706;
}

.anomaly-item.anomaly .anomaly-badge {
  background: #ef444420;
  color: #dc2626;
}
</style>

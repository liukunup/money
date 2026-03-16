<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTransactionsStore } from '@/stores/transactions';
import AnomalyMarker from '@/components/anomaly/AnomalyMarker.vue';
import Button from '@/components/ui/Button.vue';

const { t } = useI18n();
const transactionsStore = useTransactionsStore();

const filterLevel = ref<string>('all');

onMounted(async () => {
  await transactionsStore.fetchAnomalies();
});

const filteredTransactions = computed(() => {
  if (filterLevel.value === 'all') {
    return transactionsStore.anomalies;
  }
  return transactionsStore.anomalies.filter(
    (t: any) => t.anomaly_info?.anomaly_level === filterLevel.value
  );
});

const statistics = computed(() => transactionsStore.anomalyStatistics);

const formatCurrency = (amount: number): string => {
  const locale = localStorage.getItem('locale') || 'zh-CN';
  return new Intl.NumberFormat(locale === 'en-US' ? 'en-US' : 'zh-CN', {
    style: 'currency',
    currency: locale === 'en-US' ? 'USD' : 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};
</script>

<template>
  <div class="anomaly-list-view">
    <header class="header">
      <h1>{{ t('anomaly.title') }}</h1>
      <p class="subtitle">{{ t('anomaly.subtitle') }}</p>
    </header>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card warning">
        <div class="stat-icon">⚠️</div>
        <div class="stat-value">{{ statistics.warning }}</div>
        <div class="stat-label">{{ t('anomaly.warning') }}</div>
      </div>
      <div class="stat-card anomaly">
        <div class="stat-icon">🔴</div>
        <div class="stat-value">{{ statistics.anomaly }}</div>
        <div class="stat-label">{{ t('anomaly.anomaly') }}</div>
      </div>
      <div class="stat-card alert">
        <div class="stat-icon">🚨</div>
        <div class="stat-value">{{ statistics.alert }}</div>
        <div class="stat-label">{{ t('anomaly.alert') }}</div>
      </div>
    </div>

    <!-- Filter -->
    <div class="filter-bar">
      <select v-model="filterLevel" class="filter-select">
        <option value="all">{{ t('anomaly.all') }}</option>
        <option value="warning">{{ t('anomaly.warning') }}</option>
        <option value="anomaly">{{ t('anomaly.anomaly') }}</option>
        <option value="alert">{{ t('anomaly.alert') }}</option>
      </select>
    </div>

    <!-- Transaction List -->
    <div class="transaction-list">
      <div 
        v-for="transaction in filteredTransactions" 
        :key="transaction.id"
        class="transaction-row"
      >
        <div class="transaction-info">
          <div class="transaction-amount">
            -{{ transaction.amount }}
          </div>
          <div class="transaction-note">
            {{ transaction.note || 'Unknown' }}
          </div>
          <div class="transaction-date">
            {{ transaction.date }}
          </div>
        </div>
        <AnomalyMarker 
          v-if="transaction.anomaly_info?.anomaly_level"
          :level="transaction.anomaly_info.anomaly_level"
          :reason="transaction.anomaly_info.anomaly_reason"
        />
      </div>
      
      <div v-if="filteredTransactions.length === 0" class="empty-state">
        <div class="empty-icon">✅</div>
        <p class="empty-text">{{ t('anomaly.noAnomalies') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.anomaly-list-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: var(--color-surface-primary);
  border-radius: 16px;
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.filter-bar {
  margin-bottom: 16px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--color-separator);
  border-radius: 8px;
  font-size: 14px;
  background: var(--color-surface-primary);
}

.transaction-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.transaction-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-surface-primary);
  border-radius: 12px;
}

.transaction-amount {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-expense);
}

.transaction-note {
  font-size: 14px;
  color: var(--color-text-primary);
}

.transaction-date {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: var(--color-text-secondary);
}
</style>

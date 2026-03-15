<template>
  <div class="dashboard" ref="dashboardRef">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="dashboard-title">{{ t('dashboard.title') }}</h1>
          <p class="dashboard-subtitle">{{ t('dashboard.subtitle') }}</p>
        </div>
        <div class="header-actions">
          <button
            class="action-btn"
            @click="handleDownload"
            :title="t('dashboard.downloadScreenshot')"
            :aria-label="t('dashboard.downloadScreenshot')"
          >
            <span class="action-icon">📥</span>
          </button>
          <button
            class="action-btn"
            @click="handleShare"
            :title="t('dashboard.share')"
            :aria-label="t('dashboard.share')"
          >
            <span class="action-icon">📤</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Summary Cards -->
    <section v-if="!transactionsStore.loading" class="summary-cards">
      <Card variant="elevated" class="summary-card balance-card">
        <div class="card-content">
          <div class="card-label">{{ t('dashboard.currentBalance') }}</div>
          <div class="card-value" :class="{ positive: balance >= 0, negative: balance < 0 }">
            {{ formatCurrency(balance) }}
          </div>
          <div class="card-trend">
            <span v-if="balance >= 0">{{ t('dashboard.positive') }}</span>
            <span v-else class="negative">{{ t('dashboard.negative') }}</span>
          </div>
        </div>
      </Card>

      <Card variant="elevated" class="summary-card income-card">
        <div class="card-content">
          <div class="card-label">{{ t('dashboard.incomeThisMonth') }}</div>
          <div class="card-value positive">
            +{{ formatCurrency(totalIncome) }}
          </div>
          <div class="card-trend">
            {{ transactionCount }} {{ transactionCount !== 1 ? t('dashboard.transactions') : t('dashboard.transaction') }}
          </div>
        </div>
      </Card>

      <Card variant="elevated" class="summary-card expense-card">
        <div class="card-content">
          <div class="card-label">{{ t('dashboard.expenseThisMonth') }}</div>
          <div class="card-value negative">
            -{{ formatCurrency(totalExpense) }}
          </div>
          <div class="card-trend">
            {{ t('dashboard.avgPerDay', { amount: formatCurrency(averageDailyExpense) }) }}
          </div>
        </div>
      </Card>
    </section>

    <!-- Skeleton Loading -->
    <section v-else class="summary-cards skeleton">
      <Card v-for="i in 3" :key="i" variant="elevated" class="summary-card">
        <div class="skeleton-content">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line value"></div>
          <div class="skeleton-line subtitle"></div>
        </div>
      </Card>
    </section>

    <!-- Recent Transactions -->
    <section class="recent-transactions">
      <div class="section-header">
        <h2 class="section-title">{{ t('dashboard.recentTransactions') }}</h2>
        <Button
          variant="tertiary"
          size="small"
          @click="$router.push('/transactions')"
        >
          {{ t('common.viewAll') }}
        </Button>
      </div>

      <div v-if="transactionsStore.loading" class="skeleton-list">
        <div v-for="i in 3" :key="i" class="skeleton-item">
          <div class="skeleton-icon"></div>
          <div class="skeleton-content">
            <div class="skeleton-line title"></div>
            <div class="skeleton-line subtitle"></div>
          </div>
        </div>
      </div>

      <div v-else-if="recentTransactions.length === 0" class="empty-state">
        <div class="empty-icon">💸</div>
        <p class="empty-message">{{ t('dashboard.noTransactions') }}</p>
        <Button variant="primary" @click="showAddModal = true">
          {{ t('dashboard.addFirstTransaction') }}
        </Button>
      </div>

      <div v-else class="transactions-list">
        <TransactionItem
          v-for="transaction in recentTransactions"
          :key="transaction.id"
          :transaction="transaction"
          @edit="handleEditTransaction"
          @delete="handleDeleteTransaction"
        />
      </div>
    </section>

    <!-- Quick Add FAB -->
    <Button
      v-if="!transactionsStore.loading"
      class="fab"
      variant="primary"
      size="large"
      @click="showAddModal = true"
      aria-label="Add transaction"
    >
      <span class="fab-icon">+</span>
    </Button>

    <!-- Transaction Form Modal -->
    <TransactionFormModal
      v-if="showAddModal"
      :transaction="editingTransaction ?? undefined"
      @close="handleCloseModal"
      @save="handleSaveTransaction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import TransactionItem from '@/components/transaction/TransactionItem.vue'
import TransactionFormModal from '@/components/transaction/TransactionFormModal.vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useStatistics } from '@/composables/useStatistics'
import { captureAndDownload, captureAndShare } from '@/utils/screenshot'
import type { Transaction, TransactionCreate, TransactionUpdate } from '@/types/models'

const transactionsStore = useTransactionsStore()
const { t } = useI18n()

const dashboardRef = ref<HTMLElement | null>(null)
const isCapturing = ref(false)

const {
  balance,
  totalIncome,
  totalExpense,
  transactionCount,
  recentTransactions,
  averageDailyExpense,
} = useStatistics()

const showAddModal = ref(false)
const editingTransaction = ref<Transaction | undefined>(undefined)

const formatCurrency = (amount: number): string => {
  const locale = localStorage.getItem('locale') || 'zh-CN'
  return new Intl.NumberFormat(locale === 'en-US' ? 'en-US' : 'zh-CN', {
    style: 'currency',
    currency: locale === 'en-US' ? 'USD' : 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

const handleEditTransaction = (id: number) => {
  const transaction = transactionsStore.transactions.find(t => t.id === id)
  if (transaction) {
    editingTransaction.value = transaction
    showAddModal.value = true
  }
}

const handleDeleteTransaction = async (id: number) => {
  const transaction = transactionsStore.transactions.find(t => t.id === id)
  if (transaction && confirm(t('transactions.deleteConfirm'))) {
    await transactionsStore.deleteTransaction(id)
  }
}

const handleSaveTransaction = async (data: TransactionCreate) => {
  if (editingTransaction.value) {
    const updateData: TransactionUpdate = {
      amount: data.amount,
      type: data.type,
      category_id: data.category_id,
      date: data.date,
      note: data.note,
    }
    await transactionsStore.updateTransaction(editingTransaction.value.id, updateData)
  } else {
    await transactionsStore.createTransaction(data)
  }
  handleCloseModal()
}

const handleCloseModal = () => {
  showAddModal.value = false
  editingTransaction.value = undefined
}

const handleDownload = async () => {
  if (!dashboardRef.value || isCapturing.value) return
  
  isCapturing.value = true
  try {
    const filename = `money-dashboard-${new Date().toISOString().split('T')[0]}.png`
    await captureAndDownload(dashboardRef.value, filename)
  } catch (error) {
    console.error('Failed to download screenshot:', error)
  } finally {
    isCapturing.value = false
  }
}

const handleShare = async () => {
  if (!dashboardRef.value || isCapturing.value) return
  
  isCapturing.value = true
  try {
    await captureAndShare(
      dashboardRef.value,
      t('dashboard.shareTitle'),
      t('dashboard.shareText')
    )
  } catch (error) {
    console.error('Failed to share screenshot:', error)
  } finally {
    isCapturing.value = false
  }
}

transactionsStore.fetchTransactions()
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 100px;
}

.dashboard-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-text {
  flex: 1;
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-separator-opaque);
  background: var(--color-bg-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-default);
}

.action-btn:hover {
  background: var(--color-bg-tertiary);
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  font-size: 18px;
}

.dashboard-title {
  font-size: 34px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.dashboard-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.summary-card {
  background: var(--color-surface-primary);
  border-radius: var(--radius-xl);
  padding: 20px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px var(--color-shadow-lg);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  letter-spacing: -0.2px;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -1px;
  transition: color 0.2s ease;
}

.card-value.positive {
  color: var(--color-success);
}

.card-value.negative {
  color: var(--color-destructive);
}

.card-trend {
  font-size: 13px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.card-trend .negative {
  color: var(--color-destructive);
}

.skeleton-content {
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

.skeleton-line.subtitle {
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

.recent-transactions {
  background: var(--color-surface-primary);
  border-radius: var(--radius-xl);
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.3px;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-surface-secondary);
  border-radius: var(--radius-lg);
}

.skeleton-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  background: linear-gradient(
    90deg,
    var(--color-surface-tertiary) 25%,
    var(--color-surface-secondary) 50%,
    var(--color-surface-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-message {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0 0 24px 0;
}

.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px var(--color-shadow-md);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  z-index: var(--z-index-fab);
}

.fab:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px var(--color-shadow-lg);
}

.fab:active {
  transform: scale(0.95);
}

.fab-icon {
  font-size: 32px;
  font-weight: 300;
  line-height: 1;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }

  .dashboard-title {
    font-size: 28px;
  }

  .dashboard-subtitle {
    font-size: 15px;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .card-value {
    font-size: 28px;
  }

  .recent-transactions {
    padding: 16px;
  }

  .section-title {
    font-size: 20px;
  }

  .fab {
    width: 50px;
    height: 50px;
    bottom: 20px;
    right: 20px;
  }

  .fab-icon {
    font-size: 28px;
  }

  .header-actions {
    gap: var(--space-1);
  }

  .action-btn {
    width: 36px;
    height: 36px;
  }

  .action-icon {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 12px;
  }

  .summary-card {
    padding: 16px;
  }

  .card-value {
    font-size: 24px;
  }

  .fab {
    width: 48px;
    height: 48px;
    bottom: 16px;
    right: 16px;
  }
}
</style>

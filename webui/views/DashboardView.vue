<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <h1 class="dashboard-title">Dashboard</h1>
      <p class="dashboard-subtitle">Your financial overview</p>
    </header>

    <!-- Summary Cards -->
    <section v-if="!transactionsStore.loading" class="summary-cards">
      <Card variant="elevated" class="summary-card balance-card">
        <div class="card-content">
          <div class="card-label">Current Balance</div>
          <div class="card-value" :class="{ positive: balance >= 0, negative: balance < 0 }">
            {{ formatCurrency(balance) }}
          </div>
          <div class="card-trend">
            <span v-if="balance >= 0">Positive</span>
            <span v-else class="negative">Negative</span>
          </div>
        </div>
      </Card>

      <Card variant="elevated" class="summary-card income-card">
        <div class="card-content">
          <div class="card-label">Income (This Month)</div>
          <div class="card-value positive">
            +{{ formatCurrency(totalIncome) }}
          </div>
          <div class="card-trend">
            {{ transactionCount }} transaction{{ transactionCount !== 1 ? 's' : '' }}
          </div>
        </div>
      </Card>

      <Card variant="elevated" class="summary-card expense-card">
        <div class="card-content">
          <div class="card-label">Expense (This Month)</div>
          <div class="card-value negative">
            -{{ formatCurrency(totalExpense) }}
          </div>
          <div class="card-trend">
            Avg. {{ formatCurrency(averageDailyExpense) }}/day
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
        <h2 class="section-title">Recent Transactions</h2>
        <Button
          variant="tertiary"
          size="small"
          @click="$router.push('/transactions')"
        >
          View All
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
        <p class="empty-message">No transactions yet</p>
        <Button variant="primary" @click="showAddModal = true">
          Add Your First Transaction
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
      :transaction="editingTransaction"
      @close="handleCloseModal"
      @save="handleSaveTransaction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import TransactionItem from '@/components/transaction/TransactionItem.vue'
import TransactionFormModal from '@/components/transaction/TransactionFormModal.vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useStatistics } from '@/composables/useStatistics'
import type { Transaction } from '@/types/models'

const router = useRouter()
const transactionsStore = useTransactionsStore()

// Use statistics composable
const {
  balance,
  totalIncome,
  totalExpense,
  transactionCount,
  recentTransactions,
  averageDailyExpense,
} = useStatistics()

// Modal state
const showAddModal = ref(false)
const editingTransaction = ref<Transaction | null>(null)

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

// Handle edit transaction
const handleEditTransaction = (transaction: Transaction) => {
  editingTransaction.value = transaction
  showAddModal.value = true
}

// Handle delete transaction
const handleDeleteTransaction = async (transaction: Transaction) => {
  if (confirm(`Delete transaction "${transaction.note || 'No note'}"?`)) {
    await transactionsStore.deleteTransaction(transaction.id)
  }
}

// Handle save transaction
const handleSaveTransaction = async (data: Partial<Transaction>) => {
  if (editingTransaction.value) {
    await transactionsStore.updateTransaction(editingTransaction.value.id, data)
  } else {
    await transactionsStore.createTransaction(data)
  }
  handleCloseModal()
}

// Handle close modal
const handleCloseModal = () => {
  showAddModal.value = false
  editingTransaction.value = null
}

// Load transactions on mount
transactionsStore.fetchTransactions()
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 100px; /* Space for FAB */
}

/* Header */
.dashboard-header {
  margin-bottom: 32px;
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

/* Summary Cards */
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

/* Skeleton Loading */
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

/* Recent Transactions */
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

/* Skeleton List */
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

/* Empty State */
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

/* FAB */
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

/* Responsive Design */
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

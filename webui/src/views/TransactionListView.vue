<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTransactionsStore } from '@/stores/transactions';
import { useCategoriesStore } from '@/stores/categories';
import { useTagsStore } from '@/stores/tags';
import { useAuthStore } from '@/stores/auth';
import type { Transaction, TransactionFilters } from '@/types';
import TransactionFormModal from '@/components/transaction/TransactionFormModal.vue';
import TransactionItem from '@/components/transaction/TransactionItem.vue';
import Button from '@/components/ui/Button.vue';

const { t } = useI18n();
const transactionsStore = useTransactionsStore();
const categoriesStore = useCategoriesStore();
const tagsStore = useTagsStore();
const authStore = useAuthStore();

const showFormModal = ref(false);
const editingTransaction = ref<number | null>(null);

onMounted(async () => {
  authStore.checkAuth();
  await Promise.all([
    categoriesStore.fetchCategories('expense'),
    tagsStore.fetchTags(),
    transactionsStore.fetchTransactions(),
  ]);
});

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  const locale = localStorage.getItem('locale') || 'zh-CN';
  return date.toLocaleDateString(locale === 'en-US' ? 'en-US' : 'zh-CN', {
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  });
};

const groupedTransactions = computed(() => {
  const groups = new Map<string, Transaction[]>();

  function addTransactionToGroups(transaction: Transaction) {
    const date = formatDate(transaction.date);
    if (!groups.has(date)) {
      groups.set(date, []);
    }
    groups.get(date)!.push(transaction);
  }

  transactionsStore.transactions.forEach(addTransactionToGroups);

  return Array.from(groups.entries())
    .sort((a, b) => {
      return new Date(b[0]).getTime() - new Date(a[0]).getTime();
    })
    .map(([date, transactions]) => ({ date, transactions }));
});

function handleAdd() {
  editingTransaction.value = null;
  showFormModal.value = true;
}

function handleEdit(id: number) {
  editingTransaction.value = id;
  showFormModal.value = true;
}

async function handleDelete(id: number) {
  if (confirm(t('transactions.deleteConfirm'))) {
    try {
      await transactionsStore.deleteTransaction(id);
    } catch (error) {
      console.error('Failed to delete transaction:', error);
    }
  }
}

function handleFormClose() {
  showFormModal.value = false;
  editingTransaction.value = null;
}

function applyFilters() {
  transactionsStore.fetchTransactions({
    type: filterType.value || undefined,
    category_id: filterCategoryId.value || undefined,
    tag_id: filterTagId.value || undefined,
    start_date: filterStartDate.value || undefined,
    end_date: filterEndDate.value || undefined,
  });
}

function clearFilters() {
  filterType.value = undefined;
  filterCategoryId.value = undefined;
  filterTagId.value = undefined;
  filterStartDate.value = undefined;
  filterEndDate.value = undefined;
  transactionsStore.clearFilters();
  applyFilters();
}

const filterType = ref<'income' | 'expense'>();

const expenseCategories = computed(() => categoriesStore.expenseCategories);
const incomeCategories = computed(() => categoriesStore.incomeCategories);
const allCategories = computed(() => {
  const placeholder = { id: 0, name: t('transactions.allTypes'), type: 'expense' as const, icon: undefined, created_at: '' };
  return [
    placeholder,
    ...expenseCategories.value,
    ...incomeCategories.value,
  ];
});

const filterCategoryId = ref<number>();
const filterTagId = ref<number>();

const filterStartDate = ref<string>();
const filterEndDate = ref<string>();

const hasActiveFilters = computed(() => {
  return !!filterType.value || !!filterCategoryId.value || !!filterTagId.value || !!filterStartDate.value || !!filterEndDate.value;
});
</script>

<template>
  <div class="transactions-view">
    <!-- Header -->
    <div class="header">
      <h1 class="header__title">{{ t('transactions.title') }}</h1>
      
      <Button
        variant="secondary"
        size="small"
        @click="showFormModal = true"
        class="add-btn"
      >
        + {{ t('common.add') }}
      </Button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <select v-model="filterType" class="filter-select" @change="applyFilters">
          <option :value="undefined">{{ t('transactions.allTypes') }}</option>
          <option value="expense">{{ t('transactions.expense') }}</option>
          <option value="income">{{ t('transactions.income') }}</option>
        </select>

        <select v-model="filterCategoryId" class="filter-select" @change="applyFilters">
          <option :value="undefined">{{ t('transactions.allCategories') }}</option>
          <option v-for="category in allCategories" :key="category.id" :value="category.id">
            {{ category.icon || '' }} {{ category.name }}
          </option>
        </select>

        <select v-model="filterTagId" class="filter-select" @change="applyFilters">
          <option :value="undefined">{{ t('transactions.allTags') }}</option>
          <option v-for="tag in tagsStore.tags" :key="tag.id" :value="tag.id">
            {{ tag.icon || '🏷️' }} {{ tag.name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <input
          type="date"
          v-model="filterStartDate"
          class="filter-date"
          @change="applyFilters"
        />
        <span class="filter-separator">{{ t('transactions.to') }}</span>
        <input
          type="date"
          v-model="filterEndDate"
          class="filter-date"
          @change="applyFilters"
        />
        <Button
          v-if="hasActiveFilters"
          variant="tertiary"
          size="small"
          @click="clearFilters"
        >
          {{ t('common.clear') }}
        </Button>
      </div>
    </div>

    <!-- Transactions List -->
    <div class="transactions-list">
      <div v-for="group in groupedTransactions" :key="group.date" class="date-group">
        <div class="date-header">{{ group.date }}</div>
        <div v-for="transaction in group.transactions" :key="transaction.id">
          <TransactionItem
            :transaction="transaction"
            @edit="handleEdit"
            @delete="handleDelete"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!transactionsStore.loading && transactionsStore.transactions.length === 0" class="empty-state">
        <div class="empty-icon">💰</div>
        <p class="empty-text">{{ t('transactions.noTransactions') }}</p>
        <p class="empty-subtext">{{ t('transactions.addFirst') }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="transactionsStore.loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p class="loading-text">{{ t('transactions.loading') }}</p>
      </div>
    </div>

    <!-- Form Modal -->
    <TransactionFormModal
      v-if="showFormModal"
      :transaction="editingTransaction ? transactionsStore.transactions.find(t => t.id === editingTransaction) ?? undefined : undefined"
      :mode="editingTransaction ? 'edit' : 'create'"
      @close="handleFormClose"
    />

    <!-- FAB (Floating Action Button) -->
    <button class="fab" @click="handleAdd" aria-label="Add transaction">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v6a2 2 0 1 2 2 2.2a2 2 0 1 2 2h10a2 2 0 0 1 2 2 2 2 2 2z" />
        <path stroke="white" stroke-width="2.5" d="M12 9v-1a1 1 0 0 1 1 1 0 1H6a1 1 0 0 1-1 1-1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1 1z" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.transactions-view {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
}

.header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.add-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.filters {
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-separator);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.filter-select {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-separator);
  border-radius: var(--radius-md);
  background: var(--color-bg-primary);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  min-width: 150px;
}

.filter-date {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-separator);
  border-radius: var(--radius-md);
  background: var(--color-bg-primary);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.filter-separator {
  padding: 0 var(--space-1);
  color: var(--color-text-secondary);
}

.transactions-list {
  padding: var(--space-4);
}

.date-group {
  margin-bottom: var(--space-6);
}

.date-header {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  min-height: 300px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.empty-text {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-subtext {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-separator-opaque);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

/* Floating Action Button (FAB) */
.fab {
  position: fixed;
  bottom: var(--space-8);
  right: var(--space-8);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary);
  border: none;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-normal) var(--ease-default);
  z-index: 100;
}

.fab:hover {
  background: var(--color-primary-dark);
  transform: scale(1.05);
  box-shadow: var(--shadow-xl);
}

.fab:active {
  transform: scale(0.95);
}

@media (max-width: 640px) {
  .header {
    padding: var(--space-4);
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    flex-direction: column;
    width: 100%;
  }

  .filter-select,
  .filter-date {
    width: 100%;
  }

  .fab {
    bottom: var(--space-6);
    right: var(--space-6);
  }
}
</style>

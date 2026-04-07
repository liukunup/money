<script setup lang="ts">
import { computed } from 'vue';
import type { Transaction } from '@/types';
import { useCategoriesStore } from '@/stores/categories';
import AnomalyMarker from '@/components/anomaly/AnomalyMarker.vue';

interface Props {
  transaction: Transaction;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  edit: [id: number];
  delete: [id: number];
}>();

const categoriesStore = useCategoriesStore();

function getCategoryName(categoryId: number): string {
  const category = categoriesStore.categories.find(c => c.id === categoryId);
  return category?.name || 'Unknown';
}

function getCategoryIcon(categoryId: number): string {
  const category = categoriesStore.categories.find(c => c.id === categoryId);
  return category?.icon || '💰';
}

const isExpense = computed(() => props.transaction.type === 'expense');

const amountClass = computed(() => ({
  'amount--expense': isExpense.value,
  'amount--income': !isExpense.value,
}));

const formattedDate = computed(() => {
  const date = new Date(props.transaction.date);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return 'Today';
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  }
});

const formattedAmount = computed(() => {
  const amount = parseFloat(props.transaction.amount).toFixed(2);
  return amount;
});

function handleEdit() {
  emit('edit', props.transaction.id);
}

function handleDelete() {
  emit('delete', props.transaction.id);
}
</script>

<template>
  <div class="transaction-item" :class="amountClass">
    <!-- Icon -->
    <div class="transaction-item__icon">
      {{ getCategoryIcon(props.transaction.category_id) }}
    </div>

    <!-- Main Content -->
    <div class="transaction-item__content">
      <div class="transaction-item__header">
        <span class="transaction-item__note">{{ transaction.note || getCategoryName(transaction.category_id) }}</span>
        <span class="transaction-item__date">{{ formattedDate }}</span>
      </div>
      <div class="transaction-item__amount">
        {{ isExpense ? '-' : '+' }}{{ formattedAmount }}
      </div>
      <AnomalyMarker 
        v-if="transaction.anomaly_info?.anomaly_level"
        :level="transaction.anomaly_info.anomaly_level as 'warning' | 'anomaly' | 'alert'"
        :reason="transaction.anomaly_info.anomaly_reason"
      />
    </div>

    <!-- Actions -->
    <div class="transaction-item__actions">
      <button class="action-btn" @click="handleEdit" aria-label="Edit transaction">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4H4a2 2 0 0 0-2 2v11a2 2 0 0 1 2 2 2 2 2 2h6a2 2 0 0 1-2 2 2-2l2 2 2-2a2 2 0 0 1 2 2-2 2h6a2 2 0 0 1-2 2-2l2 2 2 2a2 2 0 0 1 2 2-2h6a2 2 0 0 1-2 2 2-2l-2-2 2 2zM11 4H4a2 2 0 0 0-2 2v11a2 2 0 0 1 2 2 2h6a2 2 0 0 1-2 2 2 2l2 2 2 2a2 2 0 0 1 2 2 2h6a2 2 0 0 1-2 2 2-2l2 2 2 2a2 2 0 0 1 2 2-2h6a2 2 0 0 1-2 2 2-2zM7 12a5 5 0 0 1 5 5v10a5 5 0 0 0 1 2 2 5.5z" />
        </svg>
      </button>
      <button class="action-btn action-btn--delete" @click="handleDelete" aria-label="Delete transaction">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6h18" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 6.41L9 17.41a2 2 0 0 1-2.83-1.41 0 0 0-2.83 0 0 1 1.41-1.41L17 19.41 17.41z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.transaction-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-separator);
  transition: background var(--duration-fast) var(--ease-default);
}

.transaction-item:hover {
  background: var(--color-bg-secondary);
}

.transaction-item__icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: var(--space-3);
}

.transaction-item__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.transaction-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transaction-item__note {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  flex: 1;
}

.transaction-item__date {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.transaction-item__amount {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  text-align: right;
}

.amount--expense .transaction-item__amount {
  color: var(--color-expense);
}

.amount--income .transaction-item__amount {
  color: var(--color-income);
}

.transaction-item__actions {
  display: flex;
  gap: var(--space-2);
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-default);
}

.transaction-item:hover .transaction-item__actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  padding: var(--space-1);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
}

.action-btn:hover {
  background: var(--color-bg-tertiary);
}

.action-btn--delete {
  color: var(--color-error);
}

.action-btn--delete:hover {
  background: rgba(255, 59, 48, 0.1);
}

@media (max-width: 640px) {
  .transaction-item {
    padding: var(--space-2) var(--space-3);
  }

  .transaction-item__icon {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
}
</style>

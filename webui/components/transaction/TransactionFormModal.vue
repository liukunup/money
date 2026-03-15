<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { TransactionCreate, TransactionUpdate, Transaction, Category } from '@/types';
import { useCategoriesStore } from '@/stores/categories';
import { useTransactionsStore } from '@/stores/transactions';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';

const emit = defineEmits<{
  close: [];
  save: [data: TransactionCreate];
}>();

interface Props {
  transaction?: Transaction;
  mode?: 'create' | 'edit';
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
  transaction: undefined,
});

const categoriesStore = useCategoriesStore();
const transactionsStore = useTransactionsStore();

// Form state
const type = ref<'income' | 'expense'>('expense');
const amount = ref<number>(0);
const categoryId = ref<number>(1);
const date = ref<string>(new Date().toISOString().split('T')[0]);
const time = ref<string>(new Date().toTimeString().slice(0, 5));
const note = ref<string>('');

// Load categories on mount
categoriesStore.fetchCategories('expense');

const availableCategories = computed(() => {
  if (type.value === 'income') {
    return categoriesStore.incomeCategories;
  }
  return categoriesStore.expenseCategories;
});

const selectedCategory = computed(() => {
  return availableCategories.value.find(c => c.id === categoryId.value);
});

// Format amount for display
const formattedAmount = computed({
  get: () => {
    return amount.value.toFixed(2);
  },
  set: (value: number) => {
    amount.value = value;
  },
});

// Load transaction data if in edit mode
watch(() => props.transaction, (newTransaction) => {
  if (newTransaction && props.mode === 'edit') {
    type.value = newTransaction.type;
    amount.value = parseFloat(newTransaction.amount);
    categoryId.value = newTransaction.category_id;
    date.value = newTransaction.date;
    time.value = new Date().toTimeString().slice(0, 5);
    note.value = newTransaction.note || '';
  } else {
    // Reset form for create mode
    resetForm();
  }
}, { immediate: true });

function resetForm() {
  type.value = 'expense';
  amount.value = 0;
  categoryId.value = availableCategories.value[0]?.id || 1;
  date.value = new Date().toISOString().split('T')[0];
  time.value = new Date().toTimeString().slice(0, 5);
  note.value = '';
}

async function handleSubmit() {
  if (categoryId.value === 0) {
    return;
  }

  const data: TransactionCreate = {
    amount: amount.value,
    type: type.value,
    category_id: categoryId.value,
    date: `${date.value}T${time.value}:00`,
    note: note.value || undefined,
  };

  try {
    if (props.mode === 'edit' && props.transaction) {
      await transactionsStore.updateTransaction(props.transaction.id, data);
    } else {
      await transactionsStore.createTransaction(data);
    }
    emit('save', data);
    emit('close');
  } catch (error) {
    console.error('Failed to save transaction:', error);
  }
}

function handleClose() {
  emit('close');
  resetForm();
}
</script>

<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          {{ mode === 'edit' ? 'Edit Transaction' : 'Add Transaction' }}
        </h2>
        <button class="modal-close" @click="handleClose" aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- Type Toggle -->
        <div class="form-group">
          <div class="segmented-control">
            <button
              type="button"
              class="segmented-btn"
              :class="{ active: type === 'expense' }"
              @click="type = 'expense'"
            >
              Expense
            </button>
            <button
              type="button"
              class="segmented-btn"
              :class="{ active: type === 'income' }"
              @click="type = 'income'"
            >
              Income
            </button>
          </div>
        </div>

        <!-- Amount -->
        <div class="form-group">
          <div class="amount-display">{{ formattedAmount }}</div>
          <input
            type="number"
            v-model.number="amount"
            placeholder="0.00"
            step="0.01"
            min="0"
            required
            class="amount-input"
            aria-label="Amount"
          />
        </div>

        <!-- Category -->
        <div class="form-group">
          <Input
            v-model="categoryId"
            type="select"
            label="Category"
            required
          >
            <option v-for="category in availableCategories" :key="category.id" :value="category.id">
              {{ category.icon }} {{ category.name }}
            </option>
          </Input>
        </div>

        <!-- Date -->
        <div class="form-group">
          <Input
            v-model="date"
            type="date"
            label="Date"
            required
          />
        </div>

        <!-- Time -->
        <div class="form-group">
          <Input
            v-model="time"
            type="time"
            label="Time"
          />
        </div>

        <!-- Note -->
        <div class="form-group">
          <Input
            v-model="note"
            type="text"
            label="Note (optional)"
            placeholder="Add a note..."
          />
        </div>

        <!-- Actions -->
        <div class="form-actions">
          <Button type="button" variant="tertiary" @click="handleClose">
            Cancel
          </Button>
          <Button type="submit" variant="primary" :loading="transactionsStore.loading">
            Save
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn var(--duration-normal) var(--ease-default);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    }
  to {
    opacity: 1;
    }
}

.modal-container {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp var(--duration-normal) var(--ease-default);
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
    }
  to {
    transform: translateY(0);
    opacity: 1;
    }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6) var(--space-8);
}

.modal-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background var(--duration-fast) var(--ease-default);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: var(--color-bg-tertiary);
}

.modal-body {
  padding: 0 var(--space-8);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.segmented-control {
  display: flex;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-separator-opaque);
}

.segmented-btn {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  background: none;
  border: none;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
  cursor: pointer;
}

.segmented-btn.active {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.segmented-btn:hover:not(.active) {
  background: var(--color-separator);
}

.amount-display {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  text-align: center;
  padding: var(--space-3);
}

.amount-input {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  padding: var(--space-3);
  text-align: center;
  border: 1px solid var(--color-separator-opaque);
  border-radius: var(--radius-md);
  background: var(--color-bg-primary);
  transition: all var(--duration-fast) var(--ease-default);
}

.amount-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
}

.form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .modal-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
    animation: slideUpMobile var(--duration-normal) var(--ease-default);
  }

  @keyframes slideUpMobile {
    from {
      transform: translateY(100%);
      opacity: 0;
      }
    to {
      transform: translateY(0);
      opacity: 1;
      }
  }
}
</style>

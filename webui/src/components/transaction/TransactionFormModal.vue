<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import type { TransactionCreate, TransactionUpdate, Transaction, Category, TextParsedTransaction } from '@/types';
import { useCategoriesStore } from '@/stores/categories';
import { useTagsStore } from '@/stores/tags';
import { useTransactionsStore } from '@/stores/transactions';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';
import TextPasteInput from './TextPasteInput.vue';
import ScreenshotUpload from './ScreenshotUpload.vue';

const { t } = useI18n();

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
const tagsStore = useTagsStore();
const transactionsStore = useTransactionsStore();

const type = ref<'income' | 'expense'>('expense');
const amount = ref<number>(0);
const categoryId = ref<number>(1);
const categoryIdString = ref<string>('1');
const date = ref<string>(new Date().toISOString().split('T')[0]);
const time = ref<string>(new Date().toTimeString().slice(0, 5));
const note = ref<string>('');
const selectedTagIds = ref<number[]>([]);

// AI Input mode
const inputMode = ref<'manual' | 'text' | 'screenshot'>('manual');
const parsedData = ref<TextParsedTransaction | null>(null);

watch(categoryIdString, (newVal) => {
  categoryId.value = parseInt(newVal, 10);
});

onMounted(async () => {
  await Promise.all([
    categoriesStore.fetchCategories('expense'),
    tagsStore.fetchTags(),
  ]);
});

const availableCategories = computed(() => {
  if (type.value === 'income') {
    return categoriesStore.incomeCategories;
  }
  return categoriesStore.expenseCategories;
});

const selectedCategory = computed(() => {
  return availableCategories.value.find(c => c.id === categoryId.value);
});

const availableTags = computed(() => {
  if (type.value === 'income') {
    return tagsStore.tags.filter(t => t.type === 'income' || t.type === 'general' || !t.type);
  }
  return tagsStore.tags.filter(t => t.type === 'expense' || t.type === 'general' || !t.type);
});

const formattedAmount = computed({
  get: () => {
    return amount.value.toFixed(2);
  },
  set: (value: number) => {
    amount.value = value;
  },
});

watch(() => props.transaction, (newTransaction) => {
  if (newTransaction && props.mode === 'edit') {
    type.value = newTransaction.type;
    amount.value = parseFloat(newTransaction.amount);
    categoryId.value = newTransaction.category_id;
    date.value = newTransaction.date;
    time.value = new Date().toTimeString().slice(0, 5);
    note.value = newTransaction.note || '';
    selectedTagIds.value = newTransaction.tag_ids || [];
  } else {
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
  selectedTagIds.value = [];
}

function toggleTag(tagId: number) {
  const index = selectedTagIds.value.indexOf(tagId);
  if (index === -1) {
    selectedTagIds.value.push(tagId);
  } else {
    selectedTagIds.value.splice(index, 1);
  }
}

function handleParsedData(data: TextParsedTransaction) {
  parsedData.value = data;
  
  if (data.type) {
    type.value = data.type;
  }
  
  if (data.amount) {
    amount.value = parseFloat(data.amount);
  }
  
  if (data.date) {
    date.value = data.date;
  }
  
  if (data.note) {
    note.value = data.note;
  }
  
  // Try to match category
  if (data.category) {
    const matchedCategory = availableCategories.value.find(
      c => c.name.includes(data.category!) || data.category!.includes(c.name)
    );
    if (matchedCategory) {
      categoryId.value = matchedCategory.id;
      categoryIdString.value = String(matchedCategory.id);
    }
  }
}

function applyParsedData() {
  if (!parsedData.value) return;
  
  handleParsedData(parsedData.value);
  inputMode.value = 'manual';
  parsedData.value = null;
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
    tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined,
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
          {{ mode === 'edit' ? t('transactions.editTransaction') : t('transactions.addTransaction') }}
        </h2>
        <button class="modal-close" @click="handleClose" aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- Input Mode Toggle -->
        <div class="form-group">
          <div class="mode-toggle">
            <button
              type="button"
              class="mode-btn"
              :class="{ active: inputMode === 'manual' }"
              @click="inputMode = 'manual'"
            >
              {{ t('textParse.manual') }}
            </button>
            <button
              type="button"
              class="mode-btn"
              :class="{ active: inputMode === 'ai' }"
              @click="inputMode = 'ai'"
            >
              {{ t('textParse.aiInput') }}
            </button>
          </div>
        </div>

        <!-- AI Input Mode -->
        <div v-if="inputMode === 'ai'" class="ai-input-section">
          <TextPasteInput
            @parsed="handleParsedData"
          />
          <div v-if="parsedData" class="parsed-summary">
            <span class="parsed-amount">¥{{ parsedData.amount || '0' }}</span>
            <span class="parsed-type" :class="parsedData.type">{{ parsedData.type === 'income' ? t('transactions.income') : t('transactions.expense') }}</span>
            <button type="button" class="apply-btn" @click="applyParsedData">
              {{ t('textParse.applyToForm') }}
            </button>
          </div>
        </div>

        <!-- Manual Input Mode -->
        <template v-if="inputMode === 'manual'">
        <!-- Type Toggle -->
        <div class="form-group">
          <div class="segmented-control">
            <button
              type="button"
              class="segmented-btn"
              :class="{ active: type === 'expense' }"
              @click="type = 'expense'"
            >
              {{ t('transactions.expense') }}
            </button>
            <button
              type="button"
              class="segmented-btn"
              :class="{ active: type === 'income' }"
              @click="type = 'income'"
            >
              {{ t('transactions.income') }}
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
            v-model="categoryIdString"
            type="select"
            :label="t('transaction.category')"
            required
          >
            <option v-for="category in availableCategories" :key="category.id" :value="category.id">
              {{ category.icon }} {{ category.name }}
            </option>
          </Input>
        </div>

        <!-- Tags -->
        <div class="form-group">
          <label class="tags-label">{{ t('transaction.tags') }}</label>
          <div v-if="availableTags.length > 0" class="tags-container">
            <button
              v-for="tag in availableTags"
              :key="tag.id"
              type="button"
              :class="['tag-btn', { selected: selectedTagIds.includes(tag.id) }]"
              :style="{ '--tag-color': tag.color || '#007AFF' }"
              @click="toggleTag(tag.id)"
            >
              {{ tag.icon || '🏷️' }} {{ tag.name }}
            </button>
          </div>
          <p v-else class="no-tags">{{ t('tags.noTagsAvailable') }}</p>
        </div>

        <!-- Date -->
        <div class="form-group">
          <input
            type="date"
            v-model="date"
            class="date-input"
            label="Date"
            required
          />
          <label class="input-label">{{ t('transaction.date') }}</label>
        </div>

        <!-- Time -->
        <div class="form-group">
          <input
            type="time"
            v-model="time"
            class="time-input"
          />
          <label class="input-label">{{ t('transaction.time') }}</label>
        </div>

        <!-- Note -->
        <div class="form-group">
          <Input
            v-model="note"
            type="text"
            :label="t('transaction.noteOptional')"
            :placeholder="t('transaction.addNote')"
          />
        </div>
        </template>

        <!-- Actions -->
        <div class="form-actions">
          <Button type="button" variant="tertiary" @click="handleClose">
            {{ t('common.cancel') }}
          </Button>
          <Button type="submit" variant="primary" :loading="transactionsStore.loading">
            {{ t('common.save') }}
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

.mode-toggle {
  display: flex;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-separator-opaque);
}

.mode-btn {
  flex: 1;
  padding: var(--space-2) var(--space-4);
  background: none;
  border: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
  cursor: pointer;
}

.mode-btn.active {
  background: var(--color-primary);
  color: white;
}

.mode-btn:hover:not(.active) {
  background: var(--color-separator);
}

.ai-input-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.parsed-summary {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.parsed-amount {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.parsed-type {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.parsed-type.expense {
  background: #FFF2F0;
  color: #FF3B30;
}

.parsed-type.income {
  background: #F0FFF4;
  color: #34C759;
}

.apply-btn {
  margin-left: auto;
  padding: var(--space-1) var(--space-3);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: opacity var(--duration-fast) var(--ease-default);
}

.apply-btn:hover {
  opacity: 0.9;
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

.tags-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag-btn {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-separator);
  border-radius: var(--radius-md);
  background: var(--color-bg-primary);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.tag-btn:hover {
  border-color: var(--tag-color);
  color: var(--color-text-primary);
}

.tag-btn.selected {
  background: var(--tag-color);
  border-color: var(--tag-color);
  color: white;
}

.no-tags {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-style: italic;
}

.date-input,
.time-input {
  width: 100%;
  height: 52px;
  padding: 24px var(--space-4) var(--space-2);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-separator-opaque);
  border-radius: var(--radius-md);
  outline: none;
  transition: all var(--duration-fast) var(--ease-default);
}

.date-input:focus,
.time-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
}

.input-label {
  position: absolute;
  left: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  pointer-events: none;
  transition: all var(--duration-fast) var(--ease-default);
}

.form-group {
  position: relative;
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

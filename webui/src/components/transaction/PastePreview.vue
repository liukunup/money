<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { TextParsedTransaction } from '@/types';

const { t } = useI18n();

const props = defineProps<{
  data: TextParsedTransaction;
}>();

const emit = defineEmits<{
  apply: [];
  close: [];
}>();

const confidencePercent = computed(() => Math.round(props.data.confidence * 100));

const confidenceClass = computed(() => {
  if (props.data.confidence >= 0.8) return 'high';
  if (props.data.confidence >= 0.5) return 'medium';
  return 'low';
});

const formatTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    alipay: 'Alipay',
    wechat: 'WeChat Pay',
    sms: 'SMS',
    plain: t('textParse.plainText'),
    unknown: t('textParse.unknown'),
  };
  return labels[props.data.format_type] || props.data.format_type;
});

const transactionTypeLabel = computed(() => {
  return props.data.type === 'income' ? t('transactions.income') : t('transactions.expense');
});

function formatAmount(amount: string | null): string {
  if (!amount) return '--';
  return `¥${amount}`;
}

function formatDate(date: string | null): string {
  if (!date) return '--';
  try {
    const d = new Date(date);
    return d.toLocaleDateString('zh-CN', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit' 
    });
  } catch {
    return date;
  }
}
</script>

<template>
  <div class="paste-preview">
    <div class="preview-header">
      <h4 class="preview-title">{{ t('textParse.preview') }}</h4>
      <span class="format-badge">{{ formatTypeLabel }}</span>
    </div>

    <div class="preview-content">
      <div class="preview-row">
        <span class="preview-label">{{ t('transaction.type') }}</span>
        <span class="preview-value type-badge" :class="data.type">
          {{ transactionTypeLabel }}
        </span>
      </div>

      <div class="preview-row">
        <span class="preview-label">{{ t('transaction.amount') }}</span>
        <span class="preview-value amount" :class="{ missing: !data.amount }">
          {{ formatAmount(data.amount) }}
        </span>
      </div>

      <div class="preview-row">
        <span class="preview-label">{{ t('transaction.date') }}</span>
        <span class="preview-value" :class="{ missing: !data.date }">
          {{ formatDate(data.date) }}
        </span>
      </div>

      <div v-if="data.category" class="preview-row">
        <span class="preview-label">{{ t('transaction.category') }}</span>
        <span class="preview-value">{{ data.category }}</span>
      </div>

      <div v-if="data.merchant" class="preview-row">
        <span class="preview-label">{{ t('transaction.merchant') }}</span>
        <span class="preview-value">{{ data.merchant }}</span>
      </div>

      <div v-if="data.note" class="preview-row">
        <span class="preview-label">{{ t('transaction.note') }}</span>
        <span class="preview-value note">{{ data.note }}</span>
      </div>
    </div>

    <div class="preview-footer">
      <div class="confidence">
        <span class="confidence-label">{{ t('textParse.confidence') }}</span>
        <div class="confidence-bar">
          <div 
            class="confidence-fill" 
            :class="confidenceClass"
            :style="{ width: `${confidencePercent}%` }"
          ></div>
        </div>
        <span class="confidence-value">{{ confidencePercent }}%</span>
      </div>

      <div class="preview-actions">
        <button type="button" class="btn-secondary" @click="emit('close')">
          {{ t('common.cancel') }}
        </button>
        <button 
          type="button" 
          class="btn-primary" 
          :disabled="!data.amount"
          @click="emit('apply')"
        >
          {{ t('textParse.apply') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paste-preview {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-separator-opaque);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-tertiary);
  border-bottom: 1px solid var(--color-separator-opaque);
}

.preview-title {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.format-badge {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-sm);
}

.preview-content {
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.preview-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.preview-value {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.preview-value.missing {
  color: var(--color-text-tertiary);
}

.preview-value.note {
  font-weight: var(--font-weight-normal);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-value.amount {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.preview-value.amount.missing {
  color: var(--color-text-tertiary);
}

.type-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.type-badge.expense {
  background: #FFF2F0;
  color: #FF3B30;
}

.type-badge.income {
  background: #F0FFF4;
  color: #34C759;
}

.preview-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-separator-opaque);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.confidence {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.confidence-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.confidence-bar {
  flex: 1;
  height: 4px;
  background: var(--color-bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: 2px;
  transition: width var(--duration-normal) var(--ease-default);
}

.confidence-fill.high {
  background: #34C759;
}

.confidence-fill.medium {
  background: #FF9500;
}

.confidence-fill.low {
  background: #FF3B30;
}

.confidence-value {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  min-width: 32px;
  text-align: right;
}

.preview-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.btn-secondary:hover {
  background: var(--color-separator);
}
</style>

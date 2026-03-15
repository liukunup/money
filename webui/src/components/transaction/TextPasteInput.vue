<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { textParseService } from '@/services/text-parse.service';
import type { TextParsedTransaction } from '@/types';
import VoiceInputButton from './VoiceInputButton.vue';
import PastePreview from './PastePreview.vue';

const { t } = useI18n();

const props = defineProps<{
  modelValue?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
  parsed: [data: TextParsedTransaction];
}>();

const text = ref(props.modelValue || '');
const parsedData = ref<TextParsedTransaction | null>(null);
const isParsing = ref(false);
const parseError = ref<string | null>(null);
const showPreview = ref(false);

watch(text, (newValue) => {
  emit('update:modelValue', newValue);
});

async function handlePaste(event: ClipboardEvent) {
  const pastedText = event.clipboardData?.getData('text');
  if (pastedText) {
    await parseText(pastedText);
  }
}

async function handleTextInput() {
  if (text.value.length > 10) {
    await parseText(text.value);
  }
}

async function parseText(inputText: string) {
  if (!inputText.trim()) {
    parsedData.value = null;
    showPreview.value = false;
    return;
  }

  isParsing.value = true;
  parseError.value = null;

  try {
    const result = await textParseService.parseText(inputText);
    parsedData.value = result;
    showPreview.value = true;
    emit('parsed', result);
  } catch (error: any) {
    parseError.value = error.message || t('textParse.error');
    parsedData.value = null;
  } finally {
    isParsing.value = false;
  }
}

function handleVoiceResult(textResult: string) {
  text.value = textResult;
  parseText(textResult);
}

function handleVoiceError(error: string) {
  parseError.value = error;
}

function clearText() {
  text.value = '';
  parsedData.value = null;
  showPreview.value = false;
  parseError.value = null;
}

function applyParsedData() {
  showPreview.value = false;
}

function formatTypeLabel(type: string): string {
  return type === 'income' ? t('transactions.income') : t('transactions.expense');
}
</script>

<template>
  <div class="text-paste-input">
    <div class="input-header">
      <label class="input-label">{{ t('textParse.pasteOrSpeak') }}</label>
      <VoiceInputButton
        @result="handleVoiceResult"
        @error="handleVoiceError"
      />
    </div>

    <div class="input-container">
      <textarea
        v-model="text"
        class="paste-textarea"
        :placeholder="t('textParse.placeholder')"
        @paste="handlePaste"
        @input="handleTextInput"
        rows="3"
      ></textarea>
      
      <button
        v-if="text"
        type="button"
        class="clear-btn"
        @click="clearText"
        :title="t('common.clear')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div v-if="isParsing" class="parsing-indicator">
      <span class="spinner"></span>
      {{ t('textParse.parsing') }}
    </div>

    <div v-if="parseError" class="parse-error">
      {{ parseError }}
    </div>

    <PastePreview
      v-if="showPreview && parsedData"
      :data="parsedData"
      @apply="applyParsedData"
      @close="showPreview = false"
    />
  </div>
</template>

<style scoped>
.text-paste-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.input-container {
  position: relative;
}

.paste-textarea {
  width: 100%;
  padding: var(--space-3);
  padding-right: var(--space-10);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-separator-opaque);
  border-radius: var(--radius-md);
  resize: vertical;
  min-height: 80px;
  transition: all var(--duration-fast) var(--ease-default);
}

.paste-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
}

.paste-textarea::placeholder {
  color: var(--color-text-tertiary);
}

.clear-btn {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.clear-btn:hover {
  background: var(--color-separator);
  color: var(--color-text-primary);
}

.parsing-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-separator);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.parse-error {
  font-size: var(--font-size-sm);
  color: #FF3B30;
}
</style>

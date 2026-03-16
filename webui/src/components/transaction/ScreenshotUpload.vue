<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { ocrService, ocrResultToTextParsed, type OCRResult } from '@/services/ocr.service';
import type { TextParsedTransaction } from '@/types';
import Button from '@/components/ui/Button.vue';

const { t } = useI18n();

const emit = defineEmits<{
  parsed: [data: TextParsedTransaction];
  error: [message: string];
}>();

const isDragging = ref(false);
const isProcessing = ref(false);
const selectedFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const ocrResult = ref<OCRResult | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const errorMessage = ref<string | null>(null);

const hasResult = computed(() => ocrResult.value && ocrResult.value.success);

function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  isDragging.value = false;
  
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFileSelect(files[0]);
  }
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0]);
  }
}

async function handleFileSelect(file: File) {
  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
  const ext = file.name.split('.').pop()?.toLowerCase();
  const allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
  
  if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(ext || '')) {
    errorMessage.value = t('ocr.invalidFileType');
    return;
  }
  
  // Validate file size (max 10MB)
  if (file.size > 10 * 1024 * 1024) {
    errorMessage.value = t('ocr.fileTooLarge');
    return;
  }
  
  selectedFile.value = file;
  errorMessage.value = null;
  
  // Create preview URL
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
  previewUrl.value = URL.createObjectURL(file);
  
  // Process with OCR
  await processOCR(file);
}

async function processOCR(file: File) {
  isProcessing.value = true;
  errorMessage.value = null;
  
  try {
    const result = await ocrService.parseImage(file);
    ocrResult.value = result;
    
    if (result.success) {
      const parsed = ocrResultToTextParsed(result);
      emit('parsed', parsed);
    } else {
      errorMessage.value = result.message || t('ocr.parseFailed');
      emit('error', errorMessage.value);
    }
  } catch (error) {
    console.error('OCR processing failed:', error);
    errorMessage.value = t('ocr.processingError');
    emit('error', errorMessage.value);
  } finally {
    isProcessing.value = false;
  }
}

function clearSelection() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
  selectedFile.value = null;
  previewUrl.value = null;
  ocrResult.value = null;
  errorMessage.value = null;
  
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
}

function retry() {
  if (selectedFile.value) {
    processOCR(selectedFile.value);
  }
}
</script>

<template>
  <div class="screenshot-upload">
    <!-- Drop zone -->
    <div 
      v-if="!selectedFile"
      class="drop-zone"
      :class="{ 'drop-zone--active': isDragging }"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <div class="drop-zone__icon">📷</div>
      <p class="drop-zone__text">{{ t('ocr.dropzoneText') }}</p>
      <p class="drop-zone__subtext">{{ t('ocr.dropzoneSubtext') }}</p>
      <input 
        ref="fileInputRef"
        type="file" 
        class="drop-zone__input"
        accept="image/jpeg,image/png,image/gif,image/bmp,image/webp"
        @change="handleFileInput"
      />
      <Button variant="secondary" size="small" @click="triggerFileInput">
        {{ t('ocr.selectImage') }}
      </Button>
    </div>
    
    <!-- Preview and results -->
    <div v-else class="preview-section">
      <div class="preview-image-container">
        <img 
          v-if="previewUrl" 
          :src="previewUrl" 
          alt="Receipt preview" 
          class="preview-image"
        />
        <button class="clear-btn" @click="clearSelection" :title="t('common.clear')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Processing state -->
      <div v-if="isProcessing" class="processing">
        <div class="spinner"></div>
        <p>{{ t('ocr.processing') }}</p>
      </div>
      
      <!-- Error state -->
      <div v-else-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
        <Button variant="secondary" size="small" @click="retry">
          {{ t('common.retry') }}
        </Button>
      </div>
      
      <!-- OCR Result -->
      <div v-else-if="hasResult && ocrResult" class="ocr-result">
        <div class="result-header">
          <span class="confidence-badge" :class="{ 'high': ocrResult.confidence >= 0.7 }">
            {{ t('ocr.confidence') }}: {{ Math.round(ocrResult.confidence * 100) }}%
          </span>
          <span class="provider-badge">{{ ocrResult.provider }}</span>
        </div>
        
        <div class="result-details">
          <div v-if="ocrResult.amount" class="result-item">
            <span class="result-label">{{ t('transaction.amount') }}:</span>
            <span class="result-value amount">¥{{ ocrResult.amount }}</span>
          </div>
          <div v-if="ocrResult.date" class="result-item">
            <span class="result-label">{{ t('transaction.date') }}:</span>
            <span class="result-value">{{ ocrResult.date }}</span>
          </div>
          <div v-if="ocrResult.merchant" class="result-item">
            <span class="result-label">{{ t('ocr.merchant') }}:</span>
            <span class="result-value">{{ ocrResult.merchant }}</span>
          </div>
          <div v-if="ocrResult.category" class="result-item">
            <span class="result-label">{{ t('transaction.category') }}:</span>
            <span class="result-value">{{ ocrResult.category }}</span>
          </div>
        </div>
        
        <div class="result-actions">
          <Button variant="tertiary" size="small" @click="clearSelection">
            {{ t('common.clear') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.screenshot-upload {
  width: 100%;
}

.drop-zone {
  border: 2px dashed var(--color-separator);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  position: relative;
  transition: all var(--duration-fast);
  cursor: pointer;
  background: var(--color-bg-secondary);
}

.drop-zone:hover,
.drop-zone--active {
  border-color: var(--color-primary);
  background: var(--color-bg-primary);
}

.drop-zone__icon {
  font-size: 36px;
  margin-bottom: var(--space-3);
}

.drop-zone__text {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.drop-zone__subtext {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
}

.drop-zone__input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.preview-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.preview-image-container {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-tertiary);
}

.preview-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.clear-btn {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--duration-fast);
}

.clear-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

.processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  color: var(--color-text-secondary);
}

.spinner {
  width: 24px;
  height: 24px;
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

.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-error);
}

.ocr-result {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-3);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  flex-wrap: wrap;
}

.confidence-badge {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.confidence-badge.high {
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}

.provider-badge {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  text-transform: capitalize;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.result-item {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
}

.result-label {
  color: var(--color-text-secondary);
}

.result-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.result-value.amount {
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
}

.result-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-separator);
}
</style>

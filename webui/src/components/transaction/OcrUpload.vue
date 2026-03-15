<template>
  <div class="ocr-upload">
    <div 
      class="dropzone"
      :class="{ 'dropzone--active': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <span class="dropzone-icon">📷</span>
      <p>{{ t('ocr.dropOrClick') }}</p>
      <input 
        ref="fileInput"
        type="file" 
        accept="image/*" 
        @change="handleFileSelect" 
        style="display: none"
      />
    </div>

    <div v-if="previewUrl" class="preview">
      <img :src="previewUrl" alt="Preview" />
      <Button @click="clearImage" variant="ghost" size="small">
        {{ t('common.clear') }}
      </Button>
    </div>

    <div v-if="result" class="result">
      <div class="result-item">
        <label>{{ t('ocr.amount') }}</label>
        <span>¥{{ result.amount?.toFixed(2) || '-' }}</span>
      </div>
      <div class="result-item">
        <label>{{ t('ocr.date') }}</label>
        <span>{{ result.date || '-' }}</span>
      </div>
      <div class="result-item">
        <label>{{ t('ocr.merchant') }}</label>
        <span>{{ result.merchant || '-' }}</span>
      </div>
      <div class="result-item">
        <label>{{ t('ocr.category') }}</label>
        <span>{{ result.category }}</span>
      </div>
      <div class="confidence">
        <label>{{ t('ocr.confidence') }}</label>
        <div class="confidence-bar">
          <div class="confidence-fill" :style="{ width: (result.confidence * 100) + '%' }"></div>
        </div>
      </div>
      <Button @click="applyToForm" variant="primary" size="small">
        {{ t('ocr.apply') }}
      </Button>
    </div>

    <div v-if="loading" class="loading">
      {{ t('common.loading') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/Button.vue'

const { t } = useI18n()

interface OcrResult {
  amount: number | null
  date: string | null
  merchant: string | null
  category: string
  confidence: number
}

const emit = defineEmits<{
  (e: 'apply', data: { amount?: number; date?: string; note?: string; category?: string }): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const previewUrl = ref<string | null>(null)
const result = ref<OcrResult | null>(null)
const loading = ref(false)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files?.[0]) {
    processFile(target.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files?.[0]) {
    processFile(event.dataTransfer.files[0])
  }
}

const processFile = async (file: File) => {
  // Show preview
  previewUrl.value = URL.createObjectURL(file)
  loading.value = true

  try {
    // For now, use text-based parsing (no actual OCR)
    // In production, integrate with OCR API
    result.value = {
      amount: null,
      date: null,
      merchant: null,
      category: '其他',
      confidence: 0
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const clearImage = () => {
  previewUrl.value = null
  result.value = null
}

const applyToForm = () => {
  if (result.value) {
    emit('apply', {
      amount: result.value.amount || undefined,
      date: result.value.date || undefined,
      note: result.value.merchant || undefined,
      category: result.value.category
    })
  }
}
</script>

<style scoped>
.ocr-upload {
  padding: 16px;
}

.dropzone {
  border: 2px dashed var(--color-border);
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.dropzone:hover, .dropzone--active {
  border-color: var(--color-primary);
  background: var(--color-bg-secondary);
}

.dropzone-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.preview {
  margin-top: 16px;
  text-align: center;
}

.preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
}

.result {
  margin-top: 16px;
  padding: 16px;
  background: var(--color-bg-secondary);
  border-radius: 8px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.result-item label {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.confidence {
  margin-top: 12px;
}

.confidence-bar {
  height: 8px;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
}

.confidence-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s;
}

.loading {
  text-align: center;
  padding: 16px;
  color: var(--color-text-secondary);
}
</style>

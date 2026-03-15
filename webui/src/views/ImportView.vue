<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useImportsStore } from '@/stores/imports';
import { useCategoriesStore } from '@/stores/categories';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';

const { t } = useI18n();
const importsStore = useImportsStore();
const categoriesStore = useCategoriesStore();
const authStore = useAuthStore();

const isDragging = ref(false);
const selectedFile = ref<File | null>(null);
const activeTab = ref<'upload' | 'preview' | 'history' | 'files'>('upload');
const fileInputRef = ref<HTMLInputElement | null>(null);

function triggerFileInput() {
  fileInputRef.value?.click();
}

onMounted(async () => {
  authStore.checkAuth();
  await categoriesStore.fetchCategories();
  await importsStore.fetchHistory();
  await importsStore.fetchFiles();
});

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
  const allowedTypes = ['.csv', '.xlsx', '.xls'];
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  
  if (!allowedTypes.includes(ext)) {
    alert(t('import.invalidFileType'));
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) {
    alert(t('import.fileTooLarge'));
    return;
  }
  
  selectedFile.value = file;
  
  try {
    const importRecord = await importsStore.uploadFile(file);
    await importsStore.fetchPreview(importRecord.id);
    activeTab.value = 'preview';
  } catch (error) {
    console.error('Upload failed:', error);
  }
}

async function handleConfirm() {
  if (!importsStore.currentImport) return;
  
  try {
    await importsStore.confirmImport(importsStore.currentImport.id);
    selectedFile.value = null;
    await importsStore.fetchHistory();
    activeTab.value = 'history';
  } catch (error) {
    console.error('Confirm failed:', error);
  }
}

function handleCancel() {
  importsStore.clearPreview();
  selectedFile.value = null;
  activeTab.value = 'upload';
}

async function handleDownload(fileId: number) {
  await importsStore.downloadFile(fileId);
}

async function handleDeleteFile(fileId: number) {
  if (confirm(t('import.confirmDeleteFile'))) {
    await importsStore.deleteFile(fileId);
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString();
}

function formatAmount(amount: string | number): string {
  return new Number(amount).toFixed(2);
}
</script>

<template>
  <div class="import-view">
    <div class="header">
      <h1 class="header__title">{{ t('import.title') }}</h1>
    </div>

    <div class="tabs">
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'upload' }"
        @click="activeTab = 'upload'"
      >
        {{ t('import.upload') }}
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'preview' }"
        @click="activeTab = 'preview'"
        :disabled="!importsStore.preview"
      >
        {{ t('import.preview') }}
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        {{ t('import.history') }}
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'files' }"
        @click="activeTab = 'files'"
      >
        {{ t('import.files') }}
      </button>
    </div>

    <div v-if="activeTab === 'upload'" class="tab-content">
      <div 
        class="drop-zone"
        :class="{ 'drop-zone--active': isDragging }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <div class="drop-zone__icon">📁</div>
        <p class="drop-zone__text">{{ t('import.dropzoneText') }}</p>
        <p class="drop-zone__subtext">{{ t('import.dropzoneSubtext') }}</p>
        <input 
          ref="fileInputRef"
          type="file" 
          class="drop-zone__input"
          accept=".csv,.xlsx,.xls"
          @change="handleFileInput"
        />
        <Button variant="secondary" @click="triggerFileInput">
          {{ t('import.selectFile') }}
        </Button>
      </div>

      <div v-if="selectedFile" class="selected-file">
        <p>{{ selectedFile.name }}</p>
        <p class="file-size">{{ (selectedFile.size / 1024).toFixed(2) }} KB</p>
      </div>
    </div>

    <div v-if="activeTab === 'preview' && importsStore.preview" class="tab-content">
      <div class="preview-header">
        <h2>{{ importsStore.preview.file_name }}</h2>
        <div class="preview-stats">
          <span class="stat">{{ t('import.total') }}: {{ importsStore.preview.total_count }}</span>
          <span class="stat stat--income">{{ t('import.income') }}: {{ importsStore.preview.income_count }}</span>
          <span class="stat stat--expense">{{ t('import.expense') }}: {{ importsStore.preview.expense_count }}</span>
        </div>
      </div>

      <div class="preview-table">
        <table>
          <thead>
            <tr>
              <th>{{ t('import.date') }}</th>
              <th>{{ t('import.type') }}</th>
              <th>{{ t('import.amount') }}</th>
              <th>{{ t('import.category') }}</th>
              <th>{{ t('import.note') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(tx, idx) in importsStore.preview.transactions" :key="idx">
              <td>{{ formatDate(tx.date) }}</td>
              <td>
                <span :class="['type-badge', `type-badge--${tx.type}`]">
                  {{ t(`transaction.${tx.type}`) }}
                </span>
              </td>
              <td :class="['amount', `amount--${tx.type}`]">
                {{ tx.type === 'expense' ? '-' : '+' }}{{ formatAmount(tx.amount) }}
              </td>
              <td>{{ tx.category_name || '-' }}</td>
              <td class="note">{{ tx.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="preview-actions">
        <Button variant="secondary" @click="handleCancel">{{ t('common.cancel') }}</Button>
        <Button variant="primary" @click="handleConfirm">{{ t('import.confirm') }}</Button>
      </div>
    </div>

    <div v-if="activeTab === 'history'" class="tab-content">
      <div v-if="importsStore.history.length === 0" class="empty-state">
        <p>{{ t('import.noHistory') }}</p>
      </div>
      <div v-else class="history-list">
        <div v-for="record in importsStore.history" :key="record.id" class="history-item">
          <div class="history-info">
            <span class="file-name">{{ record.file_name }}</span>
            <span class="file-date">{{ formatDate(record.created_at) }}</span>
          </div>
          <div class="history-stats">
            <span class="status" :class="`status--${record.status}`">{{ record.status }}</span>
            <span class="count">{{ record.import_count }} {{ t('import.records') }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'files'" class="tab-content">
      <div v-if="importsStore.files.length === 0" class="empty-state">
        <p>{{ t('import.noFiles') }}</p>
      </div>
      <div v-else class="files-list">
        <div v-for="file in importsStore.files" :key="file.id" class="file-item">
          <div class="file-info">
            <span class="file-name">{{ file.file_name }}</span>
            <span class="file-date">{{ formatDate(file.created_at) }}</span>
          </div>
          <div class="file-actions">
            <Button variant="secondary" size="small" @click="handleDownload(file.id)">
              {{ t('import.download') }}
            </Button>
            <Button variant="tertiary" size="small" @click="handleDeleteFile(file.id)">
              {{ t('import.delete') }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.import-view {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.header {
  padding: var(--space-6);
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
}

.header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.tabs {
  display: flex;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-separator);
  padding: 0 var(--space-4);
}

.tab {
  padding: var(--space-3) var(--space-4);
  border: none;
  background: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--duration-fast);
}

.tab:hover:not(:disabled) {
  color: var(--color-text-primary);
}

.tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-content {
  padding: var(--space-6);
}

.drop-zone {
  border: 2px dashed var(--color-separator);
  border-radius: var(--radius-lg);
  padding: var(--space-12);
  text-align: center;
  position: relative;
  transition: all var(--duration-fast);
  cursor: pointer;
}

.drop-zone:hover,
.drop-zone--active {
  border-color: var(--color-primary);
  background: var(--color-bg-primary);
}

.drop-zone__icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
}

.drop-zone__text {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.drop-zone__subtext {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-4);
}

.drop-zone__input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.selected-file {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.file-size {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.preview-header {
  margin-bottom: var(--space-4);
}

.preview-stats {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-2);
}

.stat {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stat--income {
  color: var(--color-success);
}

.stat--expense {
  color: var(--color-error);
}

.preview-table {
  overflow-x: auto;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.preview-table th,
.preview-table td {
  padding: var(--space-3);
  text-align: left;
  border-bottom: 1px solid var(--color-separator);
}

.preview-table th {
  background: var(--color-bg-secondary);
  font-weight: var(--font-weight-semibold);
}

.amount--income {
  color: var(--color-success);
}

.amount--expense {
  color: var(--color-error);
}

.note {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.type-badge--income {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.type-badge--expense {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.empty-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-secondary);
}

.history-list,
.files-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.history-item,
.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.file-name {
  font-weight: var(--font-weight-medium);
}

.file-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.history-stats,
.file-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.status {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.status--confirmed {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status--pending,
.status--parsed {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.status--failed {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}
</style>

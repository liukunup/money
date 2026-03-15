import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ImportRecord, ImportPreview } from '@/types';
import { importsService } from '@/services/imports.service';

export const useImportsStore = defineStore('imports', () => {
  const currentImport = ref<ImportRecord | null>(null);
  const preview = ref<ImportPreview | null>(null);
  const history = ref<ImportRecord[]>([]);
  const files = ref<ImportRecord[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function uploadFile(file: File) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.uploadFile(file);
      currentImport.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to upload file';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPreview(importId: number) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.getPreview(importId);
      preview.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch preview';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function confirmImport(importId: number, categoryMapping?: Record<number, number>) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.confirmImport(importId, categoryMapping);
      preview.value = null;
      currentImport.value = null;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to confirm import';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchHistory(skip = 0, limit = 20) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.getHistory(skip, limit);
      history.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch history';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchFiles(skip = 0, limit = 20) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.listFiles(skip, limit);
      files.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch files';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function downloadFile(fileId: number) {
    try {
      const blob = await importsService.downloadFile(fileId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `import-${fileId}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download file:', err);
      throw err;
    }
  }

  async function deleteFile(fileId: number) {
    loading.value = true;
    error.value = null;
    try {
      await importsService.deleteFile(fileId);
      files.value = files.value.filter(f => f.id !== fileId);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to delete file';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function clearPreview() {
    preview.value = null;
    currentImport.value = null;
  }

  return {
    currentImport,
    preview,
    history,
    files,
    loading,
    error,
    uploadFile,
    fetchPreview,
    confirmImport,
    fetchHistory,
    fetchFiles,
    downloadFile,
    deleteFile,
    clearPreview,
  };
});

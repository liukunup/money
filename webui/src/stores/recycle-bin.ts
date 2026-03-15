import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { DeletedItem, RecycleBinStats } from '@/types';
import { recycleBinService } from '@/services/recycle-bin.service';

export const useRecycleBinStore = defineStore('recycleBin', () => {
  // State
  const deletedItems = ref<DeletedItem[]>([]);
  const stats = ref<RecycleBinStats>({
    total_transactions: 0,
    total_categories: 0,
    total_tags: 0,
  });
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  async function fetchDeletedItems(itemType?: string) {
    loading.value = true;
    error.value = null;
    try {
      const data = await recycleBinService.getAll(itemType);
      deletedItems.value = data;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch deleted items';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStats() {
    try {
      const data = await recycleBinService.getStats();
      stats.value = data;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch stats';
    }
  }

  async function restoreItem(item: DeletedItem) {
    loading.value = true;
    error.value = null;
    try {
      switch (item.type) {
        case 'transaction':
          await recycleBinService.restoreTransaction(item.item_id);
          break;
        case 'category':
          await recycleBinService.restoreCategory(item.item_id);
          break;
        case 'tag':
          await recycleBinService.restoreTag(item.item_id);
          break;
      }
      // Remove from local list
      deletedItems.value = deletedItems.value.filter(i => i.id !== item.id);
      await fetchStats();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to restore item';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function permanentlyDeleteItem(item: DeletedItem) {
    loading.value = true;
    error.value = null;
    try {
      switch (item.type) {
        case 'transaction':
          await recycleBinService.permanentlyDeleteTransaction(item.item_id);
          break;
        case 'category':
          await recycleBinService.permanentlyDeleteCategory(item.item_id);
          break;
        case 'tag':
          await recycleBinService.permanentlyDeleteTag(item.item_id);
          break;
      }
      // Remove from local list
      deletedItems.value = deletedItems.value.filter(i => i.id !== item.id);
      await fetchStats();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to permanently delete item';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function emptyRecycleBin(days: number = 30) {
    loading.value = true;
    error.value = null;
    try {
      await recycleBinService.empty(days);
      await fetchDeletedItems();
      await fetchStats();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to empty recycle bin';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function emptyRecycleBinAll() {
    loading.value = true;
    error.value = null;
    try {
      await recycleBinService.emptyAll();
      deletedItems.value = [];
      stats.value = {
        total_transactions: 0,
        total_categories: 0,
        total_tags: 0,
      };
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to empty recycle bin';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    deletedItems,
    stats,
    loading,
    error,
    fetchDeletedItems,
    fetchStats,
    restoreItem,
    permanentlyDeleteItem,
    emptyRecycleBin,
    emptyRecycleBinAll,
  };
});

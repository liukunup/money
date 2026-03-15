import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Tag, TagCreate, TagUpdate } from '@/types';
import { tagsService } from '@/services/tags.service';

export const useTagsStore = defineStore('tags', () => {
  // State
  const tags = ref<Tag[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const expenseTags = computed(() => tags.value.filter(t => t.type === 'expense'));
  const incomeTags = computed(() => tags.value.filter(t => t.type === 'income'));
  const generalTags = computed(() => tags.value.filter(t => t.type === 'general' || !t.type));

  // Actions
  async function fetchTags(type?: string) {
    loading.value = true;
    error.value = null;
    try {
      const data = await tagsService.getAll(type);
      tags.value = data;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch tags';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTag(data: TagCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newTag = await tagsService.create(data);
      tags.value.push(newTag);
      return newTag;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to create tag';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTag(id: number, data: TagUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await tagsService.update(id, data);
      const index = tags.value.findIndex(t => t.id === id);
      if (index !== -1) {
        tags.value[index] = updated;
      }
      return updated;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to update tag';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTag(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await tagsService.delete(id);
      tags.value = tags.value.filter(t => t.id !== id);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to delete tag';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function restoreTag(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await tagsService.restore(id);
      await fetchTags();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to restore tag';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    tags,
    loading,
    error,
    expenseTags,
    incomeTags,
    generalTags,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    restoreTag,
  };
});

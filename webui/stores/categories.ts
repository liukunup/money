import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Category, CategoryCreate } from '@/types';
import { categoriesService } from '@/services/categories.service';

export const useCategoriesStore = defineStore('categories', () => {
  // State
  const categories = ref<Category[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense'));
  const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income'));

  // Actions
  async function fetchCategories(type?: 'income' | 'expense') {
    loading.value = true;
    error.value = null;
    try {
      const data = await categoriesService.getAll(type);
      categories.value = data;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch categories';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createCategory(data: CategoryCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newCategory = await categoriesService.create(data);
      categories.value.push(newCategory);
      return newCategory;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to create category';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteCategory(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await categoriesService.delete(id);
      categories.value = categories.value.filter(c => c.id !== id);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to delete category';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    categories,
    loading,
    error,
    expenseCategories,
    incomeCategories,
    fetchCategories,
    createCategory,
    deleteCategory,
  };
});

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Transaction, TransactionCreate, TransactionUpdate, TransactionFilters } from '@/types';
import { transactionsService } from '@/services/transactions.service';

export const useTransactionsStore = defineStore('transactions', () => {
  // State
  const transactions = ref<Transaction[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const filters = ref<TransactionFilters>({});
  
  const anomalies = ref<Transaction[]>([]);
  const anomalyStatistics = ref<{
    warning: number;
    anomaly: number;
    alert: number;
    normal: number;
    total_amount: number;
  }>({
    warning: 0,
    anomaly: 0,
    alert: 0,
    normal: 0,
    total_amount: 0
  });

  // Actions
  async function fetchTransactions(fetchFilters?: TransactionFilters) {
    loading.value = true;
    error.value = null;
    try {
      const data = await transactionsService.getAll(fetchFilters || filters.value);
      transactions.value = data;
      if (fetchFilters) {
        filters.value = fetchFilters;
      }
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch transactions';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTransaction(data: TransactionCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newTransaction = await transactionsService.create(data);
      transactions.value.unshift(newTransaction);
      return newTransaction;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to create transaction';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTransaction(id: number, data: TransactionUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await transactionsService.update(id, data);
      const index = transactions.value.findIndex(t => t.id === id);
      if (index !== -1) {
        transactions.value[index] = updated;
      }
      return updated;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to update transaction';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTransaction(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await transactionsService.delete(id);
      transactions.value = transactions.value.filter(t => t.id !== id);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to delete transaction';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function setFilters(newFilters: TransactionFilters) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function clearFilters() {
    filters.value = {};
  }

  async function fetchAnomalies(fetchFilters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
  }) {
    loading.value = true;
    error.value = null;
    try {
      const params = new URLSearchParams();
      if (fetchFilters?.start_date) params.append('start_date', fetchFilters.start_date);
      if (fetchFilters?.end_date) params.append('end_date', fetchFilters.end_date);
      if (fetchFilters?.level) params.append('level', fetchFilters.level);
      
      const response = await fetch(`/api/transactions/anomalies?${params}`);
      const data = await response.json();
      
      anomalies.value = data.items || [];
      anomalyStatistics.value = data.statistics || {
        warning: 0,
        anomaly: 0,
        alert: 0,
        normal: 0,
        total_amount: 0
      };
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch anomalies';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    transactions,
    loading,
    error,
    filters,
    anomalies,
    anomalyStatistics,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    setFilters,
    clearFilters,
    fetchAnomalies,
  };
});

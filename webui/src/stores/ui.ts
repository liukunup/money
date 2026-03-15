import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export const useUIStore = defineStore('ui', () => {
  // State
  const theme = ref<'light' | 'dark' | 'auto'>('auto');
  const sidebarCollapsed = ref(false);
  const modalOpen = ref(false);
  const toastMessages = ref<ToastMessage[]>([]);

  // Actions
  function setTheme(newTheme: 'light' | 'dark' | 'auto') {
    theme.value = newTheme;
    if (newTheme !== 'auto') {
      localStorage.setItem('theme', newTheme);
    }
    applyTheme();
  }

  function applyTheme() {
    const root = document.documentElement;
    if (theme.value === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      root.setAttribute('data-theme', theme.value);
    }
  }

  function initTheme() {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'auto' | null;
    if (savedTheme) {
      theme.value = savedTheme;
    }
    applyTheme();

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'auto') {
        applyTheme();
      }
    });
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  function openModal() {
    modalOpen.value = true;
  }

  function closeModal() {
    modalOpen.value = false;
  }

  function showToast(message: ToastMessage) {
    const id = message.id || `toast-${Date.now()}`;
    toastMessages.value.push({ ...message, id });
    if (message.duration) {
      setTimeout(() => {
        dismissToast(id);
      }, message.duration);
    }
  }

  function dismissToast(id: string) {
    toastMessages.value = toastMessages.value.filter(t => t.id !== id);
  }

  return {
    theme,
    sidebarCollapsed,
    modalOpen,
    toastMessages,
    setTheme,
    initTheme,
    toggleSidebar,
    openModal,
    closeModal,
    showToast,
    dismissToast,
  };
});

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { setLocale, type LocaleType } from '@/i18n';

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export const useUIStore = defineStore('ui', () => {
  // State
  const theme = ref<'light' | 'dark' | 'auto'>('auto');
  const devicePreference = ref<'desktop' | 'mobile' | 'auto'>('auto');
  const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024);
  const sidebarCollapsed = ref(false);
  const modalOpen = ref(false);
  const toastMessages = ref<ToastMessage[]>([]);
  const locale = ref<LocaleType>('zh-CN');

  const MOBILE_BREAKPOINT = 768;

  const isMobileMode = computed(() => {
    if (devicePreference.value === 'auto') {
      return windowWidth.value < MOBILE_BREAKPOINT;
    }
    return devicePreference.value === 'mobile';
  });

  const deviceMode = computed(() => isMobileMode.value ? 'mobile' : 'desktop');

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

  function setDevicePreference(pref: 'desktop' | 'mobile' | 'auto') {
    devicePreference.value = pref;
    localStorage.setItem('devicePreference', pref);
  }

  function initDevicePreference() {
    const saved = localStorage.getItem('devicePreference') as 'desktop' | 'mobile' | 'auto' | null;
    if (saved) {
      devicePreference.value = saved;
    }
    if (typeof window !== 'undefined') {
      windowWidth.value = window.innerWidth;
    }
  }

  function updateWindowWidth() {
    if (typeof window !== 'undefined') {
      windowWidth.value = window.innerWidth;
    }
  }

  function toggleDeviceView() {
    const views: Array<'desktop' | 'mobile' | 'auto'> = ['desktop', 'mobile', 'auto'];
    const currentIndex = views.indexOf(devicePreference.value);
    const nextView = views[(currentIndex + 1) % views.length];
    setDevicePreference(nextView);
  }

  function setLocale(newLocale: LocaleType) {
    locale.value = newLocale;
    setLocale(newLocale);
  }

  function initLocale() {
    const savedLocale = localStorage.getItem('locale') as LocaleType | null;
    if (savedLocale && (savedLocale === 'zh-CN' || savedLocale === 'en-US')) {
      locale.value = savedLocale;
      setLocale(savedLocale);
    } else {
      // Default to Chinese
      locale.value = 'zh-CN';
      setLocale('zh-CN');
    }
  }

  return {
    theme,
    locale,
    devicePreference,
    deviceMode,
    isMobileMode,
    windowWidth,
    sidebarCollapsed,
    modalOpen,
    toastMessages,
    setTheme,
    initTheme,
    setLocale,
    initLocale,
    setDevicePreference,
    initDevicePreference,
    updateWindowWidth,
    toggleDeviceView,
    toggleSidebar,
    openModal,
    closeModal,
    showToast,
    dismissToast,
  };
});

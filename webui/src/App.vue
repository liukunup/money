<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import PwaInstallPrompt from '@/components/pwa/PwaInstallPrompt.vue'
import FloatingActionButton from '@/components/ui/FloatingActionButton.vue'
import BottomNavigation from '@/components/ui/BottomNavigation.vue'
import TransactionFormModal from '@/components/transaction/TransactionFormModal.vue'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const { t } = useI18n()

const showAddModal = ref(false)

onMounted(() => {
  uiStore.initTheme()
  uiStore.initDevicePreference()
  uiStore.initLocale()
  
  window.addEventListener('resize', handleResize)
  
  // Register service worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch((error) => {
        console.error('Service worker registration failed:', error)
      })
    })
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  uiStore.updateWindowWidth()
}

function toggleTheme() {
  const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto']
  const currentIndex = themes.indexOf(uiStore.theme)
  const nextTheme = themes[(currentIndex + 1) % themes.length]
  uiStore.setTheme(nextTheme)
}

function toggleDeviceView() {
  uiStore.toggleDeviceView()
}

function getThemeIcon(theme: string): string {
  switch (theme) {
    case 'light': return '☀️'
    case 'dark': return '🌙'
    default: return '⚙️'
  }
}

function getDeviceIcon(pref: string): string {
  switch (pref) {
    case 'desktop': return '🖥️'
    case 'mobile': return '📱'
    default: return '🔄'
  }
}

// Navigation items
const navItems = computed(() => [
  { path: '/dashboard', name: t('nav.dashboard'), icon: '📊' },
  { path: '/transactions', name: t('nav.transactions'), icon: '💳' },
  { path: '/categories', name: t('nav.categories'), icon: '📁' },
  { path: '/tags', name: t('nav.tags'), icon: '🏷️' },
  { path: '/budgets', name: t('nav.budgets'), icon: '💵' },
  { path: '/statistics', name: t('nav.statistics'), icon: '📈' },
  { path: '/import', name: t('nav.import'), icon: '📥' },
  { path: '/recycle-bin', name: t('nav.recycleBin'), icon: '🗑️' },
  { path: '/settings', name: t('nav.settings'), icon: '⚙️' },
  // Advanced features
  { path: '/ai-providers', name: t('nav.aiProviders'), icon: '🤖' },
  { path: '/household', name: t('nav.household'), icon: '👨‍👩‍👧‍👦' },
  { path: '/time-periods', name: t('nav.timePeriods'), icon: '📅' },
  { path: '/anomalies', name: t('nav.anomalies'), icon: '⚠️' },
])

// Check if current route requires auth
const showNav = computed(() => {
  return authStore.isAuthenticated && route.meta.requiresAuth !== false
})

// Check if route is active
const isActive = (path: string) => {
  return route.path === path || (path !== '/dashboard' && route.path.startsWith(path))
}

function handleAddClick() {
  showAddModal.value = true
}

function handleSaveTransaction() {
  showAddModal.value = false
}

function handleCloseModal() {
  showAddModal.value = false
}
</script>

<template>
  <div class="app-container">
    <!-- Navigation -->
    <nav v-if="showNav" class="nav">
      <div class="nav-brand" @click="router.push('/dashboard')">
        <span class="nav-logo">💰</span>
        <span class="nav-title">Money</span>
      </div>
      <div class="nav-items">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item--active': isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.name }}</span>
        </router-link>
      </div>
      <div class="nav-user">
        <span class="nav-user-name">{{ authStore.user?.display_name || authStore.user?.username || 'User' }}</span>
      </div>
    </nav>

    <RouterView />
    
    <!-- FAB (Mobile only) -->
    <FloatingActionButton v-if="showNav" />
    
    <!-- Bottom Navigation (Mobile only) -->
    <BottomNavigation v-if="showNav" @add-click="handleAddClick" />
    
    <!-- Global Theme Toggle -->
    <button 
      class="theme-toggle" 
      @click="toggleTheme" 
      :title="`Current: ${uiStore.theme}. Click to switch.`"
      :aria-label="`Theme: ${uiStore.theme}. Click to change.`"
    >
      <span class="theme-icon">{{ getThemeIcon(uiStore.theme) }}</span>
    </button>

    <!-- Device View Toggle -->
    <button 
      class="device-toggle" 
      @click="toggleDeviceView" 
      :title="`Current view: ${uiStore.devicePreference}. Click to switch.`"
      :aria-label="`Device view: ${uiStore.devicePreference}. Click to change.`"
    >
      <span class="device-icon">{{ getDeviceIcon(uiStore.devicePreference) }}</span>
    </button>
    
    <!-- PWA Install Prompt -->
    <PwaInstallPrompt />
    
    <!-- Transaction Form Modal -->
    <TransactionFormModal
      v-if="showAddModal"
      mode="create"
      @close="handleCloseModal"
      @save="handleSaveTransaction"
    />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: var(--color-bg-primary);
  position: relative;
}

/* Navigation */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: var(--space-6);
  padding: var(--space-3) var(--space-5);
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-separator-opaque);
  box-shadow: var(--shadow-xs);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  transition: opacity var(--duration-fast) var(--ease-default);
}

.nav-brand:hover {
  opacity: 0.8;
}

.nav-logo {
  font-size: 24px;
}

.nav-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.nav-items {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-fast) var(--ease-default);
}

.nav-item:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.nav-item--active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.nav-item--active:hover {
  background: var(--color-primary-dark);
  color: var(--color-text-inverse);
}

.nav-icon {
  font-size: 16px;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.nav-user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

/* Theme Toggle */
.theme-toggle {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: var(--color-bg-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, background-color 0.2s ease;
  z-index: 9999;
}

.theme-toggle:hover {
  transform: scale(1.05);
  background: var(--color-bg-tertiary);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.theme-icon {
  font-size: 20px;
  line-height: 1;
}

/* Device Toggle */
.device-toggle {
  position: fixed;
  top: 16px;
  right: 72px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: var(--color-bg-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, background-color 0.2s ease;
  z-index: 9999;
}

.device-toggle:hover {
  transform: scale(1.05);
  background: var(--color-bg-tertiary);
}

.device-toggle:active {
  transform: scale(0.95);
}

.device-icon {
  font-size: 20px;
  line-height: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .nav {
    padding: var(--space-2) var(--space-3);
    gap: var(--space-3);
  }

  .nav-title {
    display: none;
  }

  .nav-label {
    display: none;
  }

  .nav-item {
    padding: var(--space-2);
  }

  .nav-icon {
    font-size: 20px;
  }

  .nav-user-name {
    display: none;
  }
  
  /* Hide desktop FAB when using mobile navigation */
  :global(.fab) {
    display: none !important;
  }
}

@media (max-width: 640px) {
  .theme-toggle {
    top: 12px;
    right: 12px;
    width: 40px;
    height: 40px;
  }

  .device-toggle {
    top: 12px;
    right: 60px;
    width: 40px;
    height: 40px;
  }
  
  .theme-icon {
    font-size: 18px;
  }

  .device-icon {
    font-size: 18px;
  }
}
</style>

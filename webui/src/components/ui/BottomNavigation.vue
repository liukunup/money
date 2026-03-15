<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useUIStore } from '@/stores/ui';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const uiStore = useUIStore();

const isMobile = computed(() => uiStore.isMobileMode);

interface NavItem {
  path: string;
  name: string;
  icon: string;
  label: string;
  isAction?: boolean;
}

const navItems = computed<NavItem[]>(() => [
  { path: '/dashboard', name: 'home', icon: '🏠', label: t('nav.home') },
  { path: '/transactions', name: 'transactions', icon: '💳', label: t('nav.transactions') },
  { path: '', name: 'add', icon: '➕', label: t('transactions.add'), isAction: true },
  { path: '/statistics', name: 'statistics', icon: '📈', label: t('nav.statistics') },
  { path: '/settings', name: 'settings', icon: '⚙️', label: t('nav.settings') },
]);

function isActive(path: string): boolean {
  if (!path) return false;
  return route.path === path || (path !== '/dashboard' && route.path.startsWith(path));
}

function handleNavigation(item: NavItem) {
  if (item.isAction) {
    // The FAB will handle the add action
    // Emit event for parent to open modal
    emit('add-click');
  } else {
    router.push(item.path);
  }
}

const emit = defineEmits<{
  'add-click': [];
}>();
</script>

<template>
  <Transition name="slide-up">
    <nav v-if="isMobile" class="bottom-nav">
      <div class="bottom-nav-inner">
        <button
          v-for="item in navItems"
          :key="item.name"
          class="bottom-nav-item"
          :class="{
            'bottom-nav-item--active': isActive(item.path),
            'bottom-nav-item--action': item.isAction,
          }"
          @click="handleNavigation(item)"
        >
          <span class="bottom-nav-icon">{{ item.icon }}</span>
          <span class="bottom-nav-label">{{ item.label }}</span>
          <span v-if="item.isAction" class="bottom-nav-action-indicator"></span>
        </button>
      </div>
    </nav>
  </Transition>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-primary);
  border-top: 1px solid var(--color-separator-opaque);
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

.bottom-nav-inner {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 64px;
  max-width: 480px;
  margin: 0 auto;
  padding: 0 var(--space-2);
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: var(--space-2);
  background: none;
  border: none;
  cursor: pointer;
  flex: 1;
  max-width: 72px;
  position: relative;
  transition: all var(--duration-fast) var(--ease-default);
  border-radius: var(--radius-md);
}

.bottom-nav-item:active {
  transform: scale(0.92);
}

.bottom-nav-item--action {
  background: var(--color-primary);
  border-radius: 50%;
  width: 52px;
  height: 52px;
  margin-top: -16px;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
}

.bottom-nav-item--action:active {
  transform: scale(0.9);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
}

.bottom-nav-icon {
  font-size: 22px;
  line-height: 1;
  transition: transform var(--duration-fast) var(--ease-spring);
}

.bottom-nav-item--active .bottom-nav-icon {
  transform: scale(1.1);
}

.bottom-nav-label {
  font-size: 10px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: color var(--duration-fast) var(--ease-default);
}

.bottom-nav-item--active .bottom-nav-label {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.bottom-nav-item--action .bottom-nav-label {
  display: none;
}

.bottom-nav-item--action .bottom-nav-icon {
  font-size: 24px;
  color: var(--color-text-inverse);
}

.bottom-nav-action-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 3px;
  background: var(--color-text-inverse);
  border-radius: var(--radius-full);
  opacity: 0;
}

.bottom-nav-item--active.bottom-nav-item--action {
  background: var(--color-primary-dark);
}

/* Transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform var(--duration-normal) var(--ease-spring),
              opacity var(--duration-normal) var(--ease-default);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>

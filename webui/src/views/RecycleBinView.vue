<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRecycleBinStore } from '@/stores/recycle-bin';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';
import type { DeletedItem } from '@/types';

const { t } = useI18n();
const recycleBinStore = useRecycleBinStore();
const authStore = useAuthStore();

const filterType = ref<'all' | 'transaction' | 'category' | 'tag'>('all');

onMounted(() => {
  authStore.checkAuth();
  recycleBinStore.fetchDeletedItems();
  recycleBinStore.fetchStats();
});

async function handleRestore(item: DeletedItem) {
  try {
    await recycleBinStore.restoreItem(item);
  } catch (error) {
    console.error('Failed to restore item:', error);
  }
}

async function handlePermanentDelete(item: DeletedItem) {
  if (confirm(t('recycleBin.permanentDeleteConfirm'))) {
    try {
      await recycleBinStore.permanentlyDeleteItem(item);
    } catch (error) {
      console.error('Failed to permanently delete item:', error);
    }
  }
}

async function handleEmptyRecycleBin() {
  if (confirm(t('recycleBin.emptyOldConfirm'))) {
    try {
      await recycleBinStore.emptyRecycleBin();
    } catch (error) {
      console.error('Failed to empty recycle bin:', error);
    }
  }
}

async function handleEmptyAll() {
  if (confirm(t('recycleBin.emptyAllConfirm'))) {
    try {
      await recycleBinStore.emptyRecycleBinAll();
    } catch (error) {
      console.error('Failed to empty recycle bin:', error);
    }
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const locale = localStorage.getItem('locale') || 'zh-CN';
  return date.toLocaleDateString(locale === 'en-US' ? 'en-US' : 'zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getTypeIcon(type: string): string {
  switch (type) {
    case 'transaction':
      return '💳';
    case 'category':
      return '📁';
    case 'tag':
      return '🏷️';
    default:
      return '📄';
  }
}
</script>

<template>
  <div class="recycle-bin-view">
    <!-- Header -->
    <div class="header">
      <h1 class="header__title">{{ t('recycleBin.title') }}</h1>
      <div class="header-actions">
        <Button variant="secondary" size="small" @click="handleEmptyRecycleBin">
          {{ t('recycleBin.emptyOld') }}
        </Button>
        <Button variant="destructive" size="small" @click="handleEmptyAll">
          {{ t('recycleBin.emptyAll') }}
        </Button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats">
      <div class="stat-card">
        <span class="stat-icon">💳</span>
        <span class="stat-value">{{ recycleBinStore.stats.total_transactions }}</span>
        <span class="stat-label">{{ t('nav.transactions') }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-icon">📁</span>
        <span class="stat-value">{{ recycleBinStore.stats.total_categories }}</span>
        <span class="stat-label">{{ t('nav.categories') }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-icon">🏷️</span>
        <span class="stat-value">{{ recycleBinStore.stats.total_tags }}</span>
        <span class="stat-label">{{ t('nav.tags') }}</span>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="tabs">
      <button
        :class="{ active: filterType === 'all' }"
        @click="filterType = 'all'; recycleBinStore.fetchDeletedItems()"
      >
        {{ t('common.all') }}
      </button>
      <button
        :class="{ active: filterType === 'transaction' }"
        @click="filterType = 'transaction'; recycleBinStore.fetchDeletedItems('transaction')"
      >
        {{ t('nav.transactions') }}
      </button>
      <button
        :class="{ active: filterType === 'category' }"
        @click="filterType = 'category'; recycleBinStore.fetchDeletedItems('category')"
      >
        {{ t('nav.categories') }}
      </button>
      <button
        :class="{ active: filterType === 'tag' }"
        @click="filterType = 'tag'; recycleBinStore.fetchDeletedItems('tag')"
      >
        {{ t('nav.tags') }}
      </button>
    </div>

    <!-- Deleted Items List -->
    <div class="items-list">
      <div
        v-for="item in recycleBinStore.deletedItems"
        :key="item.id"
        class="item-card"
      >
        <div class="item-icon">{{ getTypeIcon(item.type) }}</div>
        <div class="item-info">
          <div class="item-name">{{ item.name }}</div>
          <div class="item-meta">
            <span class="item-type">{{ item.type }}</span>
            <span class="item-date">{{ item.deleted_at ? formatDate(item.deleted_at) : t('recycleBin.unknown') }}</span>
          </div>
        </div>
        <div class="item-actions">
          <Button variant="secondary" size="small" @click="handleRestore(item)">
            {{ t('recycleBin.restore') }}
          </Button>
          <Button variant="destructive" size="small" @click="handlePermanentDelete(item)">
            {{ t('recycleBin.permanentDelete') }}
          </Button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!recycleBinStore.loading && recycleBinStore.deletedItems.length === 0" class="empty-state">
        <div class="empty-icon">🗑️</div>
        <p class="empty-text">{{ t('recycleBin.empty') }}</p>
        <p class="empty-subtext">{{ t('recycleBin.emptySubtext') }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="recycleBinStore.loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p class="loading-text">{{ t('recycleBin.loading') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.recycle-bin-view {
  min-height: 100vh;
  background: var(--color-bg-secondary);
  padding: var(--space-4);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6) 0;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
}

.stat-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}

.stat-icon {
  font-size: 24px;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.tabs {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-4);
}

.tabs button {
  padding: var(--space-2) var(--space-3);
  border: none;
  background: none;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-default);
  cursor: pointer;
}

.tabs button:hover {
  color: var(--color-text-primary);
}

.tabs button.active {
  color: var(--color-primary);
  background: var(--color-bg-tertiary);
}

.items-list {
  padding: var(--space-4) var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.item-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.item-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.item-meta {
  display: flex;
  gap: var(--space-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.item-type {
  text-transform: capitalize;
}

.item-actions {
  display: flex;
  gap: var(--space-2);
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.empty-text {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-subtext {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-separator-opaque);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin-top: var(--space-3);
}

@media (max-width: 640px) {
  .stats {
    grid-template-columns: 1fr;
  }

  .item-card {
    flex-wrap: wrap;
  }

  .item-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: var(--space-2);
  }
}
</style>

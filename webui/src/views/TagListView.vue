<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTagsStore } from '@/stores/tags';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';
import TagFormModal from '@/components/tag/TagFormModal.vue';
import type { Tag } from '@/types';

const { t } = useI18n();
const tagsStore = useTagsStore();
const authStore = useAuthStore();

const showFormModal = ref(false);
const editingTag = ref<Tag | null>(null);

const filterType = ref<'all' | 'general' | 'expense' | 'income'>('all');

onMounted(() => {
  authStore.checkAuth();
  tagsStore.fetchTags();
});

const filteredTags = computed(() => {
  if (filterType.value === 'all') {
    return tagsStore.tags;
  }
  return tagsStore.tags.filter(t => t.type === filterType.value);
});

function handleAdd() {
  editingTag.value = null;
  showFormModal.value = true;
}

function handleEdit(tag: Tag) {
  editingTag.value = tag;
  showFormModal.value = true;
}

async function handleDelete(id: number) {
  if (confirm(t('tags.deleteConfirm'))) {
    try {
      await tagsStore.deleteTag(id);
    } catch (error) {
      console.error('Failed to delete tag:', error);
    }
  }
}

function handleCloseModal() {
  showFormModal.value = false;
  editingTag.value = null;
}

const colorOptions = [
  '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE',
  '#5856D6', '#00C7BE', '#FF2D55', '#8E8E93', '#636366',
];
</script>

<template>
  <div class="tags-view">
    <!-- Header -->
    <div class="header">
      <h1 class="header__title">{{ t('tags.title') }}</h1>
      <Button variant="primary" size="medium" @click="handleAdd">
        {{ t('tags.addTag') }}
      </Button>
    </div>

    <!-- Filter Tabs -->
    <div class="tabs">
      <button
        :class="{ active: filterType === 'all' }"
        @click="filterType = 'all'"
      >
        {{ t('common.all') }}
      </button>
      <button
        :class="{ active: filterType === 'general' }"
        @click="filterType = 'general'"
      >
        {{ t('tags.general') }}
      </button>
      <button
        :class="{ active: filterType === 'expense' }"
        @click="filterType = 'expense'"
      >
        {{ t('tags.expense') }}
      </button>
      <button
        :class="{ active: filterType === 'income' }"
        @click="filterType = 'income'"
      >
        {{ t('tags.income') }}
      </button>
    </div>

    <!-- Tags Grid -->
    <div class="tags-grid">
      <div
        v-for="tag in filteredTags"
        :key="tag.id"
        class="tag-card"
        @click="handleEdit(tag)"
      >
        <div class="tag-color" :style="{ backgroundColor: tag.color || '#007AFF' }"></div>
        <div class="tag-icon">{{ tag.icon || '🏷️' }}</div>
        <div class="tag-name">{{ tag.name }}</div>
        <div class="tag-type">{{ tag.type || t('tags.general') }}</div>
        <button
          class="tag-delete"
          @click.stop="handleDelete(tag.id)"
          aria-label="Delete tag"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!tagsStore.loading && tagsStore.tags.length === 0" class="empty-state">
      <div class="empty-icon">🏷️</div>
      <p class="empty-text">{{ t('tags.noTags') }}</p>
      <p class="empty-subtext">{{ t('tags.addFirst') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="tagsStore.loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ t('common.loading') }}</p>
    </div>

    <!-- Form Modal -->
    <TagFormModal
      v-if="showFormModal"
      :tag="editingTag"
      @close="handleCloseModal"
    />
  </div>
</template>

<style scoped>
.tags-view {
  min-height: 100vh;
  background: var(--color-bg-secondary);
  padding: var(--space-4);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6) 0;
}

.header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.tabs {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3);
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

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
}

.tag-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-4);
  transition: all var(--duration-normal) var(--ease-default);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  position: relative;
}

.tag-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.tag-color {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.tag-icon {
  font-size: 32px;
  margin-top: var(--space-2);
}

.tag-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.tag-type {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-transform: capitalize;
}

.tag-delete {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  background: none;
  border: none;
  padding: var(--space-1);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: color var(--duration-fast) var(--ease-default);
  cursor: pointer;
}

.tag-delete:hover {
  color: var(--color-error);
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
  margin-bottom: var(--space-6);
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
  .tags-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>

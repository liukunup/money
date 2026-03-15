<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Tag, TagCreate } from '@/types';
import { useTagsStore } from '@/stores/tags';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';

const emit = defineEmits<{
  close: [];
}>();

interface Props {
  tag?: Tag | null;
}

const props = withDefaults(defineProps<Props>(), {
  tag: null,
});

const tagsStore = useTagsStore();

// Form state
const name = ref('');
const type = ref<'general' | 'expense' | 'income'>('general');
const color = ref('#007AFF');
const icon = ref('🏷️');
const description = ref('');

// Load tag data if editing
watch(() => props.tag, (newTag) => {
  if (newTag) {
    name.value = newTag.name;
    type.value = newTag.type as 'general' | 'expense' | 'income' || 'general';
    color.value = newTag.color || '#007AFF';
    icon.value = newTag.icon || '🏷️';
    description.value = newTag.description || '';
  } else {
    resetForm();
  }
}, { immediate: true });

function resetForm() {
  name.value = '';
  type.value = 'general';
  color.value = '#007AFF';
  icon.value = '🏷️';
  description.value = '';
}

async function handleSubmit() {
  if (!name.value.trim()) {
    return;
  }

  const data: TagCreate = {
    name: name.value,
    type: type.value,
    color: color.value,
    icon: icon.value,
    description: description.value || undefined,
  };

  try {
    if (props.tag) {
      await tagsStore.updateTag(props.tag.id, data);
    } else {
      await tagsStore.createTag(data);
    }
    emit('close');
  } catch (error) {
    console.error('Failed to save tag:', error);
  }
}

function handleClose() {
  emit('close');
  resetForm();
}

// Color options
const colorOptions = [
  '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE',
  '#5856D6', '#00C7BE', '#FF2D55', '#8E8E93', '#636366',
];

// Icon options
const iconOptions = ['🏷️', '💰', '🎯', '⭐', '❤️', '🔥', '💡', '📌', '🔖', '🏅'];
</script>

<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          {{ tag ? 'Edit Tag' : 'Add Tag' }}
        </h2>
        <button class="modal-close" @click="handleClose" aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- Name -->
        <Input
          v-model="name"
          type="text"
          label="Tag Name"
          placeholder="Enter tag name"
          :required="true"
        />

        <!-- Type -->
        <div class="form-group">
          <label>Tag Type</label>
          <div class="segmented-control">
            <button
              type="button"
              :class="{ active: type === 'general' }"
              @click="type = 'general'"
            >
              General
            </button>
            <button
              type="button"
              :class="{ active: type === 'expense' }"
              @click="type = 'expense'"
            >
              Expense
            </button>
            <button
              type="button"
              :class="{ active: type === 'income' }"
              @click="type = 'income'"
            >
              Income
            </button>
          </div>
        </div>

        <!-- Color -->
        <div class="form-group">
          <label>Color</label>
          <div class="color-grid">
            <button
              v-for="colorOption in colorOptions"
              :key="colorOption"
              :class="{ 'color-btn': true, 'selected': color === colorOption }"
              :style="{ backgroundColor: colorOption }"
              @click="color = colorOption"
              type="button"
            >
              <svg v-if="color === colorOption" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Icon -->
        <div class="form-group">
          <label>Icon</label>
          <div class="icon-grid">
            <button
              v-for="iconOption in iconOptions"
              :key="iconOption"
              :class="{ 'icon-btn': true, 'selected': icon === iconOption }"
              @click="icon = iconOption"
              type="button"
            >
              {{ iconOption }}
            </button>
          </div>
        </div>

        <!-- Description -->
        <Input
          v-model="description"
          type="text"
          label="Description (optional)"
          placeholder="Enter description"
        />

        <!-- Actions -->
        <div class="form-actions">
          <Button type="button" variant="tertiary" @click="handleClose">
            Cancel
          </Button>
          <Button type="submit" variant="primary" :loading="tagsStore.loading">
            {{ tagsStore.loading ? 'Saving...' : 'Save' }}
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn var(--duration-normal) var(--ease-default);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    }
  to {
    opacity: 1;
    }
}

.modal-container {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp var(--duration-normal) var(--ease-default);
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
    }
  to {
    transform: translateY(0);
    opacity: 1;
    }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6) var(--space-8);
}

.modal-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background var(--duration-fast) var(--ease-default);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: var(--color-bg-tertiary);
}

.modal-body {
  padding: 0 var(--space-8) var(--space-8);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-group > label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.segmented-control {
  display: flex;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-separator-opaque);
}

.segmented-control button {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  background: none;
  border: none;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
  cursor: pointer;
}

.segmented-control button.active {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.segmented-control button:hover:not(.active) {
  background: var(--color-separator);
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-2);
}

.color-btn {
  width: 100%;
  aspect-ratio: 1;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--duration-fast) var(--ease-default);
}

.color-btn:hover {
  transform: scale(1.1);
}

.color-btn.selected {
  box-shadow: 0 0 0 3px var(--color-bg-primary), 0 0 0 5px currentColor;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-2);
}

.icon-btn {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
  font-size: 24px;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-default);
}

.icon-btn:hover {
  background: var(--color-bg-secondary);
}

.icon-btn.selected {
  background: var(--color-primary);
}

.form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .modal-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>

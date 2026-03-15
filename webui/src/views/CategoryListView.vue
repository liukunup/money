<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useCategoriesStore } from '@/stores/categories';
import { useAuthStore } from '@/stores/auth';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';

const { t } = useI18n();
const router = useRouter();
const categoriesStore = useCategoriesStore();
const authStore = useAuthStore();

const name = ref('');
const icon = ref('');
const type = ref<'income' | 'expense'>('expense');
const showFormModal = ref(false);
const showDeleteConfirm = ref(false);
const categoryToDelete = ref<number | null>(null);

onMounted(() => {
  authStore.checkAuth();
  categoriesStore.fetchCategories('expense');
});

const handleAdd = () => {
  name.value = '';
  icon.value = '';
  type.value = 'expense';
  showFormModal.value = true;
};

const handleEdit = (id: number) => {
  const category = categoriesStore.categories.find(c => c.id === id);
  if (!category) return;
  name.value = category.name;
  icon.value = category.icon || '';
  type.value = category.type;
  showFormModal.value = true;
  categoryToDelete.value = id;
};

const handleDeleteClick = (id: number) => {
  showDeleteConfirm.value = true;
  categoryToDelete.value = id;
};

const confirmDelete = async () => {
  if (!categoryToDelete.value) return;
  try {
    await categoriesStore.deleteCategory(categoryToDelete.value);
    showDeleteConfirm.value = false;
    categoryToDelete.value = null;
  } catch (error) {
    console.error('Failed to delete category:', error);
  }
};

const handleSubmit = async () => {
  if (!name.value.trim()) {
    return;
  }

  try {
    if (categoryToDelete.value) {
      await categoriesStore.deleteCategory(categoryToDelete.value);
      categoryToDelete.value = null;
    }

    if (categoryToDelete.value) {
      await categoriesStore.createCategory({
        name: name.value,
        type: type.value,
        icon: icon.value,
      });
    }

    showFormModal.value = false;
    name.value = '';
    icon.value = '';
    type.value = 'expense';
  } catch (error) {
    console.error('Failed to save category:', error);
  }
};

const handleCloseModal = () => {
  showFormModal.value = false;
  categoryToDelete.value = null;
  showDeleteConfirm.value = false;
};

const iconOptions = ['🍽️', '🚗', '🛒', '🎬', '🏠', '💊', '📚', '🎓', '💰', '🏡', '🎥', '💼', '🏥', '📔', '🏙', '💵', '💯'];
</script>

<template>
  <div class="categories-view">
    <!-- Header -->
    <div class="header">
      <h1 class="header__title">{{ t('categories.title') }}</h1>
      <Button
        variant="primary"
        size="medium"
        @click="handleAdd"
      >
        {{ t('categories.addCategory') }}
      </Button>
    </div>

    <!-- Income/Expense Tabs -->
    <div class="tabs">
      <button
        :class="{ 'tabs__tab': type === 'expense' ? 'tabs__tab--active' : '' }"
        @click="type = 'expense'"
      >
        {{ t('categories.expense') }}
      </button>
      <button
        :class="{ 'tabs__tab': type === 'income' ? 'tabs__tab--active' : '' }"
        @click="type = 'income'"
      >
        {{ t('categories.income') }}
      </button>
    </div>

    <!-- Categories Grid -->
    <div class="categories-grid">
      <div
        v-for="category in categoriesStore.expenseCategories"
        :key="category.id"
        class="category-card"
        @click="handleEdit(category.id)"
      >
        <div class="category-icon">{{ category.icon || '💰' }}</div>
        <div class="category-name">{{ category.name }}</div>
        <button
          class="category-delete"
          @click.stop="handleDeleteClick(category.id)"
          aria-label="Delete category"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6v-6h-12"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 6L5 12c0 0 0 1 12-1-12 1 12 2 12z"></path>
          <line x1="12" y1="12" x2="12" y2="12"></line>
          <path d="M6 18L6 18v-12c-4 0 0 1 12-1-12 2 12-12z"></path>
          </svg>
        </button>
      </div>

      <div
        v-for="category in categoriesStore.incomeCategories"
        :key="category.id"
        class="category-card"
        @click="handleEdit(category.id)"
      >
        <div class="category-icon">{{ category.icon || '💰' }}</div>
        <div class="category-name">{{ category.name }}</div>
        <button
          class="category-delete"
          @click.stop="handleDeleteClick(category.id)"
          aria-label="Delete category"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6v-6h-12"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 6L5 12c0 0 0 1 12 1 12 2 12z"></path>
            <line x1="12" y1="12" x2="12" y2="12"></line>
          </svg>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!categoriesStore.loading && categoriesStore.categories.length === 0" class="empty-state">
      <div class="empty-icon">💰</div>
      <p class="empty-text">{{ t('categories.noCategories') }}</p>
      <p class="empty-subtext">{{ t('categories.addFirst') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="categoriesStore.loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ t('common.loading') }}</p>
    </div>

    <!-- Category Form Modal -->
    <div v-if="showFormModal" class="modal-overlay" @click.self="handleCloseModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">
            {{ categoryToDelete ? t('categories.deleteCategory') : (showDeleteConfirm ? t('common.edit') : t('categories.addCategory')) }}
          </h2>
          <button class="modal-close" @click="handleCloseModal" aria-label="Close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 18v-6h12"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 6L5 12c0 0 0 1 12 1 12z"></path>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
          </button>
        </div>

        <form v-if="!showDeleteConfirm" @submit.prevent="handleSubmit" class="modal-body">
          <!-- Type -->
          <div class="form-group">
            <div class="form-group">
              <label>{{ t('categories.categoryType') }}</label>
              <div class="segmented-control">
                <button
                  type="button"
                  :class="{ active: type === 'expense' }"
                  @click="type = 'expense'"
                >
                  {{ t('categories.expense') }}
                </button>
                <button
                  type="button"
                  :class="{ active: type === 'income' }"
                  @click="type = 'income'"
                >
                  {{ t('categories.income') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Name -->
          <Input
            v-model="name"
            type="text"
            :label="t('categories.categoryName')"
            :placeholder="t('categories.categoryName')"
            :required="true"
          />

          <!-- Icon -->
          <div class="form-group">
            <label>{{ t('categories.icon') }}</label>
            <div class="icon-grid">
              <button
                v-for="iconOption in iconOptions"
                :key="iconOption"
                :class="{ 'icon-btn': true, 'selected': icon === iconOption }"
                @click="icon = iconOption"
              >
                {{ iconOption }}
              </button>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <Button type="button" variant="tertiary" @click="handleCloseModal">
              {{ t('common.cancel') }}
            </Button>
            <Button
              type="submit"
              variant="primary"
              :loading="categoriesStore.loading"
            >
              {{ categoriesStore.loading ? t('categories.saving') : t('common.save') }}
            </Button>
          </div>
        </form>

        <!-- Delete Confirmation -->
        <div v-if="showDeleteConfirm" class="delete-confirm">
          <p class="delete-confirm__message">{{ t('categories.deleteConfirm') }}</p>
          <div class="delete-confirm__actions">
            <Button
              type="button"
              variant="tertiary"
              @click="showDeleteConfirm = false"
            >
              {{ t('common.cancel') }}
            </Button>
            <Button
              type="submit"
              variant="destructive"
              :loading="categoriesStore.loading"
              @click="confirmDelete"
            >
              {{ t('common.delete') }}
            </Button>
          </div>
          </div>
        </div>
      </div>
    </div>
</template>

<style scoped>
.categories-view {
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

.tabs__tab {
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

.tabs__tab:hover {
  color: var(--color-text-primary);
}

.tabs__tab--active {
  color: var(--color-primary);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
}

.category-card {
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
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.category-icon {
  font-size: 32px;
  margin-bottom: var(--space-1);
}

.category-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.category-delete {
  margin-left: auto;
  background: none;
  border: none;
  padding: var(--space-1);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: color var(--duration-fast) var(--ease-default);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-delete:hover {
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

/* Modal */
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
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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
  padding: 0 var(--space-8);
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
  margin-bottom: var(--space-1);
}

.form-group > label:required::after {
  content: '*';
  color: var(--color-error);
  margin-left: 2px;
}

.segmented-control {
  display: flex;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-separator-opaque);
}

.segmented-btn {
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

.segmented-btn.active {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.segmented-btn:hover:not(:active) {
  background: var(--color-separator);
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(36px, 1fr));
  gap: var(--space-2);
}

.icon-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-md);
  padding: var(--space-1);
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  transition: background var(--duration-fast) var(--ease-default);
  cursor: pointer;
  font-size: 24px;
}

.icon-btn:hover {
  background: var(--color-bg-secondary);
}

.icon-btn.selected {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
  justify-content: flex-end;
}

.delete-confirm {
  text-align: center;
  padding: var(--space-6);
}

.delete-confirm__message {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
}

.delete-confirm__actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

@media (max-width: 640px) {
  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .modal-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>

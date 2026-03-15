<template>
  <div class="budget-list">
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ t('budgets.title') }}</h1>
        <p class="page-subtitle">{{ t('budgets.subtitle') }}</p>
      </div>
      <Button variant="primary" @click="openCreateModal">
        <span class="btn-icon">+</span>
        {{ t('budgets.addBudget') }}
      </Button>
    </header>

    <div v-if="budgetsStore.loading" class="loading-state">
      <Card v-for="i in 3" :key="i" variant="elevated" class="skeleton-card">
        <div class="skeleton-content">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line progress"></div>
          <div class="skeleton-line stats"></div>
        </div>
      </Card>
    </div>

    <div v-else-if="budgetsStore.budgets.length === 0" class="empty-state">
      <Card variant="elevated" class="empty-card">
        <div class="empty-content">
          <div class="empty-icon">💰</div>
          <h3 class="empty-title">{{ t('budgets.noBudgets') }}</h3>
          <p class="empty-message">{{ t('budgets.createFirst') }}</p>
          <Button variant="primary" @click="openCreateModal">
            {{ t('budgets.createBudget') }}
          </Button>
        </div>
      </Card>
    </div>

    <div v-else class="budgets-grid">
      <Card 
        v-for="budget in budgetsStore.budgets" 
        :key="budget.id" 
        variant="elevated"
        class="budget-card"
      >
        <div class="budget-card-header">
          <div class="budget-info">
            <span class="budget-icon">{{ budget.category_icon || '💰' }}</span>
            <div class="budget-details">
              <h3 class="budget-name">{{ budget.name }}</h3>
              <span class="budget-category">{{ budget.category_name || t('budgets.overall') }}</span>
            </div>
          </div>
          <div class="budget-actions">
            <button class="action-btn" @click="openEditModal(budget)" :title="t('common.edit')">
              ✏️
            </button>
            <button class="action-btn danger" @click="confirmDelete(budget)" :title="t('common.delete')">
              🗑️
            </button>
          </div>
        </div>
        
        <BudgetProgress
          :name="budget.name"
          :amount="parseFloat(budget.amount)"
          :spent="parseFloat(budget.spent)"
          :period-type="budget.period_type"
          :icon="budget.category_icon || '💰'"
        />
      </Card>
    </div>

    <BudgetFormModal
      :show="showModal"
      :budget="selectedBudget"
      @close="closeModal"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import BudgetProgress from '@/components/budget/BudgetProgress.vue'
import BudgetFormModal from '@/components/budget/BudgetFormModal.vue'
import { useBudgetsStore } from '@/stores/budgets'
import type { BudgetWithUsage, BudgetCreate, BudgetUpdate } from '@/types/models'

const { t } = useI18n()
const budgetsStore = useBudgetsStore()

const showModal = ref(false)
const selectedBudget = ref<BudgetWithUsage | null>(null)

const budgets = computed(() => budgetsStore.budgets)

const openCreateModal = () => {
  selectedBudget.value = null
  showModal.value = true
}

const openEditModal = (budget: BudgetWithUsage) => {
  selectedBudget.value = budget
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedBudget.value = null
}

const handleSubmit = async (data: BudgetCreate | BudgetUpdate) => {
  try {
    if (selectedBudget.value) {
      await budgetsStore.updateBudget(selectedBudget.value.id, data as BudgetUpdate)
    } else {
      await budgetsStore.createBudget(data as BudgetCreate)
    }
    closeModal()
    budgetsStore.fetchBudgets()
  } catch (error) {
    console.error('Failed to save budget:', error)
  }
}

const confirmDelete = async (budget: BudgetWithUsage) => {
  if (confirm(t('budgets.deleteConfirm', { name: budget.name }))) {
    try {
      await budgetsStore.deleteBudget(budget.id)
    } catch (error) {
      console.error('Failed to delete budget:', error)
    }
  }
}

onMounted(() => {
  budgetsStore.fetchBudgets()
})
</script>

<style scoped>
.budget-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 34px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0;
}

.btn-icon {
  margin-right: 4px;
}

.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.skeleton-card {
  padding: 20px;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-line {
  background: linear-gradient(
    90deg,
    var(--color-surface-tertiary) 25%,
    var(--color-surface-secondary) 50%,
    var(--color-surface-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

.skeleton-line.title {
  height: 24px;
  width: 60%;
}

.skeleton-line.progress {
  height: 8px;
  width: 100%;
}

.skeleton-line.stats {
  height: 40px;
  width: 100%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.empty-state {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.empty-card {
  max-width: 400px;
  width: 100%;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
  padding: 20px;
}

.empty-icon {
  font-size: 64px;
}

.empty-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.empty-message {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

.budgets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.budget-card {
  padding: 20px;
}

.budget-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.budget-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.budget-icon {
  font-size: 28px;
}

.budget-details {
  display: flex;
  flex-direction: column;
}

.budget-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.budget-category {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.budget-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 16px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 1;
}

.action-btn.danger:hover {
  filter: grayscale(1);
}

@media (max-width: 768px) {
  .budget-list {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-title {
    font-size: 28px;
  }

  .budgets-grid {
    grid-template-columns: 1fr;
  }
}
</style>
<template>
  <Modal :show="show" @close="$emit('close')" :title="isEditing ? 'Edit Budget' : 'Create Budget'">
    <form @submit.prevent="handleSubmit" class="budget-form">
      <div class="form-group">
        <label for="name">Budget Name</label>
        <Input
          id="name"
          v-model="form.name"
          type="text"
          placeholder="e.g., Monthly Groceries"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="category">Category (Optional)</label>
        <select id="category" v-model="form.category_id" class="select-input">
          <option :value="null">Overall Budget (No Category)</option>
          <option 
            v-for="cat in categories" 
            :key="cat.id" 
            :value="cat.id"
          >
            {{ cat.icon || '' }} {{ cat.name }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="amount">Budget Amount</label>
        <Input
          id="amount"
          :model-value="form.amount > 0 ? String(form.amount) : ''"
          @update:model-value="form.amount = Number($event) || 0"
          type="number"
          min="1"
          step="0.01"
          placeholder="0.00"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="period">Budget Period</label>
        <select id="period" v-model="form.period_type" class="select-input">
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="start_date">Start Date</label>
          <Input
            id="start_date"
            v-model="form.start_date"
            type="date"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="end_date">End Date (Optional)</label>
          <Input
            id="end_date"
            v-model="form.end_date"
            type="date"
          />
        </div>
      </div>
      
      <div v-if="isEditing" class="form-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="isActive" />
          <span>Active Budget</span>
        </label>
      </div>
      
      <div class="form-actions">
        <Button variant="secondary" type="button" @click="$emit('close')">
          Cancel
        </Button>
        <Button variant="primary" type="submit" :loading="loading">
          {{ isEditing ? 'Update' : 'Create' }} Budget
        </Button>
      </div>
    </form>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import { useCategoriesStore } from '@/stores/categories'
import type { BudgetCreate, BudgetUpdate, BudgetWithUsage } from '@/types/models'

interface Props {
  show: boolean
  budget?: BudgetWithUsage | null
}

const props = withDefaults(defineProps<Props>(), {
  budget: null,
})

const emit = defineEmits<{
  close: []
  submit: [data: BudgetCreate | BudgetUpdate]
}>()

const categoriesStore = useCategoriesStore()
const categories = computed(() => categoriesStore.expenseCategories)

const form = ref({
  name: '',
  category_id: null as number | null,
  amount: 0,
  period_type: 'monthly' as 'weekly' | 'monthly' | 'yearly',
  start_date: new Date().toISOString().split('T')[0],
  end_date: '',
})

const isActive = ref(true)
const loading = ref(false)

const isEditing = computed(() => !!props.budget)

watch(() => props.show, (show) => {
  if (show && props.budget) {
    form.value = {
      name: props.budget.name,
      category_id: props.budget.category_id || null,
      amount: parseFloat(props.budget.amount),
      period_type: props.budget.period_type,
      start_date: props.budget.start_date,
      end_date: props.budget.end_date || '',
    }
    isActive.value = props.budget.is_active === 1
  } else if (show) {
    form.value = {
      name: '',
      category_id: null,
      amount: 0,
      period_type: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
    }
    isActive.value = true
  }
})

const handleSubmit = async () => {
  loading.value = true
  try {
    const data: BudgetCreate | BudgetUpdate = {
      ...form.value,
      end_date: form.value.end_date || undefined,
      category_id: form.value.category_id ?? undefined,
    }
    
    if (isEditing.value && props.budget) {
      emit('submit', { ...data, is_active: isActive.value ? 1 : 0 })
    } else {
      emit('submit', data)
    }
  } finally {
    loading.value = false
  }
}

categoriesStore.fetchCategories()
</script>

<style scoped>
.budget-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.select-input {
  padding: 10px 12px;
  font-size: 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-primary);
  color: var(--color-text-primary);
  appearance: none;
  cursor: pointer;
}

.select-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-alpha);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label span {
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
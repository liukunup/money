<template>
  <div class="time-periods-page">
    <div class="page-header">
      <h1>{{ t('timePeriods.title') }}</h1>
      <Button @click="openModal()" variant="primary">
        {{ t('timePeriods.add') }}
      </Button>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    
    <div v-else-if="timePeriods.length === 0" class="empty-state">
      <span class="empty-icon">📅</span>
      <p>{{ t('timePeriods.empty') }}</p>
    </div>

    <div v-else class="periods-list">
      <Card v-for="period in timePeriods" :key="period.id">
        <div class="period-item">
          <div class="period-info">
            <span class="period-icon">{{ getIcon(period.type) }}</span>
            <div class="period-details">
              <h3>{{ period.name }}</h3>
              <p class="period-type">{{ t('timePeriods.types.' + period.type) }}</p>
              <p v-if="period.start_date && period.end_date" class="period-dates">
                {{ formatDate(period.start_date) }} - {{ formatDate(period.end_date) }}
              </p>
            </div>
          </div>
          <div class="period-actions">
            <Button @click="openModal(period)" size="small" variant="ghost">✏️</Button>
            <Button @click="deletePeriod(period.id)" size="small" variant="danger">🗑️</Button>
          </div>
        </div>
      </Card>
    </div>

    <!-- Modal -->
    <Modal v-if="showModal" @close="closeModal" :title="editingPeriod ? t('timePeriods.edit') : t('timePeriods.add')">
      <form @submit.prevent="savePeriod">
        <Input v-model="form.name" :label="t('timePeriods.name')" required />
        
        <div class="form-group">
          <label>{{ t('timePeriods.type') }}</label>
          <select v-model="form.type" class="select">
            <option value="custom">{{ t('timePeriods.types.custom') }}</option>
            <option value="monthly">{{ t('timePeriods.types.monthly') }}</option>
            <option value="quarterly">{{ t('timePeriods.types.quarterly') }}</option>
            <option value="yearly">{{ t('timePeriods.types.yearly') }}</option>
          </select>
        </div>

        <div v-if="form.type === 'custom'" class="form-group">
          <label>{{ t('timePeriods.dateRange') }}</label>
          <div class="date-range">
            <Input v-model="form.start_date" type="date" :label="t('timePeriods.startDate')" />
            <Input v-model="form.end_date" type="date" :label="t('timePeriods.endDate')" />
          </div>
        </div>

        <div class="form-group">
          <label>{{ t('timePeriods.color') }}</label>
          <div class="color-picker">
            <button 
              v-for="c in colors" 
              :key="c"
              type="button"
              class="color-btn"
              :class="{ active: form.color === c }"
              :style="{ background: c }"
              @click="form.color = c"
            />
          </div>
        </div>

        <div class="modal-actions">
          <Button type="submit" variant="primary">{{ t('common.save') }}</Button>
          <Button @click="closeModal" variant="ghost">{{ t('common.cancel') }}</Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '@/components/ui/Modal.vue'

const { t } = useI18n()

interface TimePeriod {
  id: number
  name: string
  type: string
  start_date?: string
  end_date?: string
  color?: string
}

const timePeriods = ref<TimePeriod[]>([])
const loading = ref(true)
const showModal = ref(false)
const editingPeriod = ref<TimePeriod | null>(null)

const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']

const form = ref({
  name: '',
  type: 'custom',
  start_date: '',
  end_date: '',
  color: colors[0]
})

const getIcon = (type: string) => {
  const icons: Record<string, string> = {
    custom: '📆',
    monthly: '📅',
    quarterly: '📊',
    yearly: '📆'
  }
  return icons[type] || '📅'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const fetchPeriods = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/time-periods/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      timePeriods.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const openModal = (period?: TimePeriod) => {
  if (period) {
    editingPeriod.value = period
    form.value = {
      name: period.name,
      type: period.type,
      start_date: period.start_date || '',
      end_date: period.end_date || '',
      color: period.color || colors[0]
    }
  } else {
    editingPeriod.value = null
    form.value = {
      name: '',
      type: 'custom',
      start_date: '',
      end_date: '',
      color: colors[0]
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPeriod.value = null
}

const savePeriod = async () => {
  try {
    const url = editingPeriod.value 
      ? `/api/time-periods/${editingPeriod.value.id}`
      : '/api/time-periods/'
    const method = editingPeriod.value ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    if (res.ok) {
      closeModal()
      fetchPeriods()
    }
  } catch (e) {
    console.error(e)
  }
}

const deletePeriod = async (id: number) => {
  if (!confirm(t('timePeriods.confirmDelete'))) return
  try {
    const res = await fetch(`/api/time-periods/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      fetchPeriods()
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchPeriods()
})
</script>

<style scoped>
.time-periods-page {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: 48px;
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: 48px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.periods-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.period-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.period-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.period-icon {
  font-size: 24px;
}

.period-details h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.period-type, .period-dates {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 4px 0 0;
}

.period-actions {
  display: flex;
  gap: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  background: var(--color-bg);
  color: var(--color-text);
}

.date-range {
  display: flex;
  gap: 12px;
}

.color-picker {
  display: flex;
  gap: 8px;
}

.color-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
}

.color-btn.active {
  border-color: var(--color-text);
  transform: scale(1.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
</style>

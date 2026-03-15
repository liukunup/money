<template>
  <div class="household-page">
    <div class="page-header">
      <h1>{{ t('household.title') }}</h1>
    </div>

    <!-- No Household -->
    <div v-if="!household" class="no-household">
      <div class="empty-state">
        <span class="empty-icon">👨‍👩‍👧‍👦</span>
        <p>{{ t('household.notInHousehold') }}</p>
      </div>
      
      <div class="action-buttons">
        <Button @click="showCreateModal = true" variant="primary">
          {{ t('household.createHousehold') }}
        </Button>
        <Button @click="showJoinModal = true" variant="secondary">
          {{ t('household.joinHousehold') }}
        </Button>
      </div>
    </div>

    <!-- Has Household -->
    <div v-else class="household-info">
      <Card>
        <template #header>
          <div class="household-header">
            <h2>{{ household.name }}</h2>
            <span class="role-badge">{{ t('household.role.' + userRole) }}</span>
          </div>
        </template>
        
        <div class="invite-section">
          <label>{{ t('household.inviteCode') }}</label>
          <div class="invite-code">
            <code>{{ household.invite_code }}</code>
            <Button @click="copyInviteCode" size="small" variant="ghost">
              📋
            </Button>
            <Button @click="regenerateCode" size="small" variant="ghost">
              🔄
            </Button>
          </div>
        </div>

        <div class="members-section">
          <h3>{{ t('household.members') }} ({{ members.length }})</h3>
          <List>
            <ListItem v-for="member in members" :key="member.id">
              <div class="member-info">
                <span class="member-name">{{ member.user?.display_name || member.user?.username }}</span>
                <span class="member-role">{{ t('household.role.' + member.role) }}</span>
              </div>
              <Button 
                v-if="canRemove(member)" 
                @click="removeMember(member.id)" 
                size="small" 
                variant="danger"
              >
                {{ t('common.remove') }}
              </Button>
            </ListItem>
          </List>
        </div>

        <div class="actions">
          <Button v-if="userRole === 'owner'" @click="showEditModal = true" variant="secondary">
            {{ t('household.editName') }}
          </Button>
          <Button v-if="userRole !== 'owner'" @click="leaveHousehold" variant="danger">
            {{ t('household.leave') }}
          </Button>
          <Button v-if="userRole === 'owner'" @click="deleteHousehold" variant="danger">
            {{ t('household.delete') }}
          </Button>
        </div>
      </Card>
    </div>

    <!-- Create Modal -->
    <Modal v-if="showCreateModal" @close="showCreateModal = false" :title="t('household.createHousehold')">
      <form @submit.prevent="createHousehold">
        <Input v-model="createForm.name" :label="t('household.name')" required />
        <div class="modal-actions">
          <Button type="submit" variant="primary">{{ t('common.create') }}</Button>
          <Button @click="showCreateModal = false" variant="ghost">{{ t('common.cancel') }}</Button>
        </div>
      </form>
    </Modal>

    <!-- Join Modal -->
    <Modal v-if="showJoinModal" @close="showJoinModal = false" :title="t('household.joinHousehold')">
      <form @submit.prevent="joinHousehold">
        <Input v-model="joinForm.inviteCode" :label="t('household.inviteCode')" required />
        <div class="modal-actions">
          <Button type="submit" variant="primary">{{ t('household.join') }}</Button>
          <Button @click="showJoinModal = false" variant="ghost">{{ t('common.cancel') }}</Button>
        </div>
      </form>
    </Modal>

    <!-- Edit Modal -->
    <Modal v-if="showEditModal" @close="showEditModal = false" :title="t('household.editName')">
      <form @submit.prevent="updateHousehold">
        <Input v-model="editForm.name" :label="t('household.name')" required />
        <div class="modal-actions">
          <Button type="submit" variant="primary">{{ t('common.save') }}</Button>
          <Button @click="showEditModal = false" variant="ghost">{{ t('common.cancel') }}</Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUIStore } from '@/stores/ui'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '@/components/ui/Modal.vue'
import List from '@/components/ui/List.vue'
import ListItem from '@/components/ui/ListItem.vue'

const { t } = useI18n()
const uiStore = useUIStore()

interface Member {
  id: number
  user_id: number
  role: string
  user?: {
    id: number
    username: string
    display_name?: string
  }
}

interface Household {
  id: number
  name: string
  invite_code: string
  members: Member[]
}

const household = ref<Household | null>(null)
const members = ref<Member[]>([])
const userRole = ref<string>('member')

const showCreateModal = ref(false)
const showJoinModal = ref(false)
const showEditModal = ref(false)

const createForm = ref({ name: '' })
const joinForm = ref({ inviteCode: '' })
const editForm = ref({ name: '' })

const currentUserId = computed(() => uiStore.user?.id)

const fetchHousehold = async () => {
  try {
    const res = await fetch('/api/households/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      household.value = await res.json()
      editForm.value.name = household.value?.name || ''
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchMembers = async () => {
  try {
    const res = await fetch('/api/households/members', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      members.value = await res.json()
      const me = members.value.find(m => m.user_id === currentUserId.value)
      userRole.value = me?.role || 'member'
    }
  } catch (e) {
    console.error(e)
  }
}

const createHousehold = async () => {
  try {
    const res = await fetch('/api/households/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(createForm.value)
    })
    if (res.ok) {
      showCreateModal.value = false
      createForm.value = { name: '' }
      await fetchHousehold()
      await fetchMembers()
    }
  } catch (e) {
    console.error(e)
  }
}

const joinHousehold = async () => {
  try {
    const res = await fetch('/api/households/join', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ invite_code: joinForm.value.inviteCode })
    })
    if (res.ok) {
      showJoinModal.value = false
      joinForm.value = { inviteCode: '' }
      await fetchHousehold()
      await fetchMembers()
    }
  } catch (e) {
    console.error(e)
  }
}

const updateHousehold = async () => {
  try {
    const res = await fetch(`/api/households/${household.value?.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editForm.value)
    })
    if (res.ok) {
      showEditModal.value = false
      await fetchHousehold()
    }
  } catch (e) {
    console.error(e)
  }
}

const leaveHousehold = async () => {
  if (!confirm(t('household.confirmLeave'))) return
  try {
    const res = await fetch('/api/households/leave', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      household.value = null
      members.value = []
    }
  } catch (e) {
    console.error(e)
  }
}

const deleteHousehold = async () => {
  if (!confirm(t('household.confirmDelete'))) return
  try {
    const res = await fetch(`/api/households/${household.value?.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      household.value = null
      members.value = []
    }
  } catch (e) {
    console.error(e)
  }
}

const removeMember = async (memberId: number) => {
  try {
    const res = await fetch(`/api/households/members/${memberId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      await fetchMembers()
    }
  } catch (e) {
    console.error(e)
  }
}

const copyInviteCode = () => {
  navigator.clipboard.writeText(household.value?.invite_code || '')
}

const regenerateCode = async () => {
  try {
    const res = await fetch('/api/households/regenerate-code', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      household.value!.invite_code = data.invite_code
    }
  } catch (e) {
    console.error(e)
  }
}

const canRemove = (member: Member) => {
  if (userRole.value === 'owner' && member.role !== 'owner') return true
  if (userRole.value === 'admin' && member.role === 'member') return true
  return false
}

onMounted(() => {
  fetchHousehold()
  fetchMembers()
})
</script>

<style scoped>
.household-page {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

.household-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.household-header h2 {
  font-size: 20px;
  font-weight: 600;
}

.role-badge {
  background: var(--color-primary);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.invite-section {
  margin: 24px 0;
}

.invite-section label {
  display: block;
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.invite-code {
  display: flex;
  align-items: center;
  gap: 8px;
}

.invite-code code {
  background: var(--color-bg-secondary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 18px;
  letter-spacing: 2px;
}

.members-section {
  margin: 24px 0;
}

.members-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.member-name {
  font-weight: 500;
}

.member-role {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
</style>

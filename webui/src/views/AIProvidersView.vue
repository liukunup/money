<template>
  <div class="ai-providers-view">
    <div class="page-header">
      <h1>AI Providers</h1>
      <button class="btn-primary" @click="showAddModal = true">
        Add Provider
      </button>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else-if="providers.length === 0" class="empty-state">
      <p>No AI providers configured</p>
      <p class="hint">Add an AI provider to enable smart classification</p>
    </div>

    <div v-else class="provider-list">
      <div 
        v-for="provider in providers" 
        :key="provider.id" 
        class="provider-card"
        :class="{ inactive: !provider.is_active }"
      >
        <div class="provider-header">
          <div class="provider-info">
            <span class="provider-name">{{ provider.name }}</span>
            <span class="provider-type">{{ provider.provider_type }}</span>
          </div>
          <div class="provider-status">
            <span 
              class="status-badge" 
              :class="{ active: provider.is_active }"
            >
              {{ provider.is_active ? 'Active' : 'Inactive' }}
            </span>
            <span class="priority">Priority: {{ provider.priority }}</span>
          </div>
        </div>
        
        <div class="provider-details">
          <div class="detail-row">
            <span class="label">Base URL:</span>
            <span class="value">{{ provider.base_url }}</span>
          </div>
          <div v-if="provider.models?.length" class="detail-row">
            <span class="label">Models:</span>
            <span class="value">{{ provider.models.join(', ') }}</span>
          </div>
        </div>
        
        <div class="provider-actions">
          <button 
            class="btn-icon" 
            @click="toggleProvider(provider.id)"
            :title="provider.is_active ? 'Disable' : 'Enable'"
          >
            {{ provider.is_active ? 'Disable' : 'Enable' }}
          </button>
          <button class="btn-icon" @click="editProvider(provider)">Edit</button>
          <button class="btn-icon danger" @click="deleteProvider(provider.id)">Delete</button>
        </div>
      </div>
    </div>

    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ showEditModal ? 'Edit Provider' : 'Add Provider' }}</h2>
        
        <form @submit.prevent="saveProvider">
          <div class="form-group">
            <label>Name</label>
            <input v-model="formData.name" type="text" required />
          </div>
          
          <div class="form-group">
            <label>Provider Type</label>
            <select v-model="formData.provider_type" required @change="applyDefaults">
              <option value="">Select provider...</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="ollama">Ollama</option>
              <option value="deepseek">DeepSeek</option>
              <option value="azure">Azure OpenAI</option>
              <option value="moonshot">Moonshot AI</option>
              <option value="zhipu">Zhipu AI</option>
              <option value="minimax">MiniMax</option>
              <option value="qianwen">Qianwen (Alibaba)</option>
              <option value="tongyi">Tongyi (Alibaba)</option>
              <option value="spark">iFlytek Spark</option>
              <option value="hunyuan">Tencent Hunyuan</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Base URL</label>
            <input v-model="formData.base_url" type="text" required />
          </div>
          
          <div class="form-group">
            <label>API Key</label>
            <input v-model="formData.api_key" type="password" />
          </div>
          
          <div class="form-group">
            <label>Models (comma-separated)</label>
            <input v-model="modelsInput" type="text" placeholder="gpt-4, gpt-3.5-turbo" />
          </div>
          
          <div class="form-group">
            <label>Priority (1-1000, lower = higher priority)</label>
            <input v-model.number="formData.priority" type="number" min="1" max="1000" />
          </div>
          
          <div class="form-group checkbox">
            <label>
              <input v-model="formData.is_active" type="checkbox" />
              Active
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { aiService } from '@/services/ai.service';
import type { AIProvider, AIProviderCreate, AIProviderUpdate } from '@/types/models';

const providers = ref<AIProvider[]>([]);
const loading = ref(true);
const showAddModal = ref(false);
const showEditModal = ref(false);
const editingId = ref<number | null>(null);

const formData = ref<AIProviderCreate>({
  name: '',
  provider_type: '',
  base_url: '',
  api_key: '',
  models: [],
  is_active: true,
  priority: 100
});

const modelsInput = ref('');

const defaultUrls: Record<string, string> = {
  openai: 'https://api.openai.com/v1',
  anthropic: 'https://api.anthropic.com/v1',
  ollama: 'http://localhost:11434/v1',
  deepseek: 'https://api.deepseek.com/v1',
  moonshot: 'https://api.moonshot.cn/v1',
  zhipu: 'https://open.bigmodel.cn/api/paas/v4',
  minimax: 'https://api.minimax.chat/v1',
  qianwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  tongyi: 'https://dashscope.aliyuncs.com/api/v1',
  spark: 'https://spark-api.xf-yun.com/v3.5',
  hunyuan: 'https://hunyuan.cloud.tencent.com'
};

const loadProviders = async () => {
  try {
    loading.value = true;
    providers.value = await aiService.getProviders(true);
  } catch (error) {
    console.error('Failed to load providers:', error);
  } finally {
    loading.value = false;
  }
};

const applyDefaults = () => {
  if (formData.value.provider_type && defaultUrls[formData.value.provider_type]) {
    formData.value.base_url = defaultUrls[formData.value.provider_type];
  }
};

const saveProvider = async () => {
  try {
    const models = modelsInput.value ? modelsInput.value.split(',').map(m => m.trim()) : [];
    
    if (showEditModal.value && editingId.value) {
      const updateData: AIProviderUpdate = {
        name: formData.value.name,
        provider_type: formData.value.provider_type,
        base_url: formData.value.base_url,
        api_key: formData.value.api_key,
        models,
        is_active: formData.value.is_active,
        priority: formData.value.priority
      };
      await aiService.updateProvider(editingId.value, updateData);
    } else {
      const createData: AIProviderCreate = {
        name: formData.value.name,
        provider_type: formData.value.provider_type,
        base_url: formData.value.base_url,
        api_key: formData.value.api_key,
        models,
        is_active: formData.value.is_active,
        priority: formData.value.priority
      };
      await aiService.createProvider(createData);
    }
    
    closeModal();
    await loadProviders();
  } catch (error) {
    console.error('Failed to save provider:', error);
  }
};

const editProvider = (provider: AIProvider) => {
  editingId.value = provider.id;
  formData.value = {
    name: provider.name,
    provider_type: provider.provider_type,
    base_url: provider.base_url,
    api_key: provider.api_key || '',
    models: provider.models || [],
    is_active: provider.is_active,
    priority: provider.priority
  };
  modelsInput.value = provider.models?.join(', ') || '';
  showEditModal.value = true;
};

const toggleProvider = async (id: number) => {
  try {
    await aiService.toggleProvider(id);
    await loadProviders();
  } catch (error) {
    console.error('Failed to toggle provider:', error);
  }
};

const deleteProvider = async (id: number) => {
  if (!confirm('Are you sure you want to delete this provider?')) return;
  
  try {
    await aiService.deleteProvider(id);
    await loadProviders();
  } catch (error) {
    console.error('Failed to delete provider:', error);
  }
};

const closeModal = () => {
  showAddModal.value = false;
  showEditModal.value = false;
  editingId.value = null;
  formData.value = {
    name: '',
    provider_type: '',
    base_url: '',
    api_key: '',
    models: [],
    is_active: true,
    priority: 100
  };
  modelsInput.value = '';
};

onMounted(loadProviders);
</script>

<style scoped>
.ai-providers-view {
  padding: 20px;
  max-width: 800px;
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

.btn-primary {
  background: #007AFF;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state .hint {
  font-size: 14px;
  color: #999;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-card {
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 16px;
}

.provider-card.inactive {
  opacity: 0.6;
}

.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.provider-name {
  font-size: 18px;
  font-weight: 600;
}

.provider-type {
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.provider-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #ff3b30;
  color: white;
}

.status-badge.active {
  background: #34c759;
}

.priority {
  font-size: 12px;
  color: #999;
}

.provider-details {
  margin-bottom: 12px;
}

.detail-row {
  display: flex;
  gap: 8px;
  font-size: 14px;
  margin-bottom: 4px;
}

.detail-row .label {
  color: #666;
  min-width: 80px;
}

.provider-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: #f5f5f5;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.btn-icon.danger {
  color: #ff3b30;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
}

.modal h2 {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-secondary {
  background: #f5f5f5;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}
</style>

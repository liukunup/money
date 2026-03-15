# AI Capabilities Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement AI-powered features including provider management, transaction classification, and spending suggestions.

**Architecture:** OpenAI-compatible API wrapper with fallback strategy. Multiple providers supported with priority-based selection.

**Tech Stack:** 
- Backend: FastAPI, SQLAlchemy, httpx (async HTTP)
- Frontend: Vue 3, Pinia, TypeScript

---

## Phase 1: Backend Implementation

### Task 1: Create AIProvider Model

**Files:**
- Create: `app/models/ai_provider.py`
- Modify: `app/models/__init__.py`

**Step 1: Create model file**

```python
# app/models/ai_provider.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class AIProvider(Base):
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    provider_type = Column(String(20), nullable=False)
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(255))
    models = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 2: Update models/__init__.py**

Add: `from app.models.ai_provider import AIProvider`

---

### Task 2: Create AIProvider Schema

**Files:**
- Create: `app/schemas/ai_provider.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class AIProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    provider_type: str = Field(..., pattern="^(openai|deepseek|ollama|anthropic|google|azure|mistral|cohere|together|localai|llamafile|jan)$")
    base_url: str
    api_key: Optional[str] = None
    models: List[str] = []
    is_active: bool = True
    priority: int = 100

class AIProviderCreate(AIProviderBase):
    pass

class AIProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    models: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class AIProviderResponse(AIProviderBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AIProviderTestRequest(BaseModel):
    provider_type: str
    base_url: str
    api_key: str
    model: str = "default"

class AIProviderTestResponse(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[int] = None
```

---

### Task 3: Create AIService

**Files:**
- Create: `app/services/ai_service.py`

**Step 1: Write the service**

```python
import httpx
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.ai_provider import AIProvider
from app.models.category import Category

CLASSIFICATION_PROMPT = """You are a financial category classifier for personal expenses.
Available categories: {categories}

Classify this transaction:
- Amount: {amount}
- Note: {note}
- Date: {date}

Respond with ONLY valid JSON (no other text):
{{"category": "餐饮", "confidence": 0.95}}"""

class AIService:
    def __init__(self, db: Session):
        self.db = db
    
    def _get_active_providers(self) -> List[AIProvider]:
        return self.db.query(AIProvider).filter(
            AIProvider.is_active == True
        ).order_by(AIProvider.priority.asc()).all()
    
    async def _call_provider(
        self, 
        provider: AIProvider, 
        messages: List[Dict], 
        model: str = None
    ) -> Optional[str]:
        """Call a single provider, return response or None on failure"""
        import time
        start = time.time()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider.api_key}"
        }
        
        # Use first model if not specified
        if not model and provider.models:
            model = provider.models[0]
        elif not model:
            model = "default"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{provider.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Provider {provider.name} failed: {e}")
            return None
    
    async def chat(
        self, 
        messages: List[Dict], 
        model: str = None
    ) -> Optional[str]:
        """Chat with fallback: try providers in priority order"""
        providers = self._get_active_providers()
        
        for provider in providers:
            result = await self._call_provider(provider, messages, model)
            if result:
                return result
        
        return None
    
    async def classify_transaction(
        self, 
        note: str, 
        amount: float, 
        date: str,
        categories: List[str]
    ) -> Dict[str, Any]:
        """Classify a transaction using AI"""
        category_list = ", ".join(categories)
        prompt = CLASSIFICATION_PROMPT.format(
            categories=category_list,
            amount=amount,
            note=note,
            date=date
        )
        
        messages = [{"role": "user", "content": prompt}]
        result = await self.chat(messages)
        
        if not result:
            return {"category": "其他", "confidence": 0.0, "error": "All providers failed"}
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "category": data.get("category", "其他"),
                    "confidence": data.get("confidence", 0.0)
                }
        except:
            pass
        
        return {"category": "其他", "confidence": 0.0, "error": "Failed to parse response"}
    
    async def get_suggestions(
        self, 
        transactions: List[Dict]
    ) -> List[str]:
        """Get spending suggestions based on transaction history"""
        if not transactions:
            return []
        
        total_expense = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
        total_income = sum(t.get("amount", 0) for t in transactions if t.get("type") == "income")
        
        prompt = f"""You are a financial advisor. Analyze this user's spending:
- Total expenses: ¥{total_expense}
- Total income: ¥{total_income}
- Transaction count: {len(transactions)}

Provide 2-3 brief, actionable suggestions in Chinese. Be specific with numbers.
Respond with ONLY a JSON array: ["suggestion1", "suggestion2"]"""

        messages = [{"role": "user", "content": prompt}]
        result = await self.chat(messages)
        
        if not result:
            return ["Add more transactions to get AI suggestions"]
        
        try:
            import re
            json_match = re.search(r'\[[^\]]+\]', result)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions[:3]
        except:
            pass
        
        return ["Unable to generate suggestions at this time"]
    
    @staticmethod
    async def test_connection(
        provider_type: str,
        base_url: str,
        api_key: str,
        model: str = "default"
    ) -> Dict[str, Any]:
        """Test connection to a provider"""
        import time
        start = time.time()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                latency = int((time.time() - start) * 1000)
                
                if response.status_code == 200:
                    return {"success": True, "message": "Connection successful", "latency_ms": latency}
                else:
                    return {"success": False, "message": f"Error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
```

---

### Task 4: Create AI API Routes

**Files:**
- Create: `app/api/ai.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.ai_provider import AIProvider
from app.models.category import Category
from app.schemas.ai_provider import (
    AIProviderCreate, 
    AIProviderUpdate, 
    AIProviderResponse,
    AIProviderTestRequest,
    AIProviderTestResponse
)
from app.services.ai_service import AIService

router = APIRouter()

# === Admin API: Provider Management ===

@router.get("/providers", response_model=List[AIProviderResponse])
def get_providers(db: Session = Depends(get_db)):
    """List all AI providers"""
    providers = db.query(AIProvider).order_by(AIProvider.priority.asc()).all()
    return providers

@router.post("/providers", response_model=AIProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(provider: AIProviderCreate, db: Session = Depends(get_db)):
    """Create a new AI provider"""
    db_provider = AIProvider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.put("/providers/{provider_id}", response_model=AIProviderResponse)
def update_provider(
    provider_id: int, 
    provider: AIProviderUpdate, 
    db: Session = Depends(get_db)
):
    """Update an AI provider"""
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    update_data = provider.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_provider, field, value)
    
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    """Delete an AI provider"""
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db.delete(db_provider)
    db.commit()
    return None

@router.post("/providers/test", response_model=AIProviderTestResponse)
async def test_provider(request: AIProviderTestRequest):
    """Test connection to an AI provider"""
    result = await AIService.test_connection(
        request.provider_type,
        request.base_url,
        request.api_key,
        request.model
    )
    return result

# === AI API: User-facing ===

@router.post("/classify")
async def classify_transaction(
    note: str,
    amount: float,
    date: str,
    db: Session = Depends(get_db)
):
    """Classify a transaction using AI"""
    # Get all categories
    categories = db.query(Category).filter(Category.is_deleted == False).all()
    category_names = [c.name for c in categories]
    
    ai_service = AIService(db)
    result = await ai_service.classify_transaction(note, amount, date, category_names)
    return result

@router.get("/suggestions")
async def get_suggestions(
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Get AI-powered spending suggestions"""
    from app.models.transaction import Transaction
    
    # Get recent transactions
    transactions = db.query(Transaction).filter(
        Transaction.is_deleted == False
    ).limit(limit).all()
    
    transaction_data = [
        {
            "amount": float(t.amount),
            "type": t.type,
            "note": t.note,
            "date": str(t.date)
        }
        for t in transactions
    ]
    
    ai_service = AIService(db)
    suggestions = await ai_service.get_suggestions(transaction_data)
    return {"suggestions": suggestions}
```

---

### Task 5: Register AI Routes in Main App

**Files:**
- Modify: `app/main.py`

Add import: `from app.api import users, categories, transactions, ai`
Add router: `app.include_router(ai.router, prefix="/api/ai", tags=["ai"])`

---

### Task 6: Run Database Migration

**Step 1: Initialize new database with AIProvider table**

```bash
cd /Users/liukunup/Documents/repo/money
python -c "
from app.db.database import Base, engine
from app.models.ai_provider import AIProvider
Base.metadata.create_all(bind=engine)
print('AIProvider table created')
"
```

---

## Phase 2: Frontend Implementation

### Task 7: Create AI Store

**Files:**
- Create: `webui/src/stores/ai.ts`

```typescript
import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface AIProvider {
  id: number
  name: string
  provider_type: string
  base_url: string
  api_key?: string
  models: string[]
  is_active: boolean
  priority: number
  created_at: string
}

export const useAIStore = defineStore('ai', {
  state: () => ({
    providers: [] as AIProvider[],
    loading: false,
    error: null as string | null,
    suggestions: [] as string[],
    autoClassify: localStorage.getItem('autoClassify') === 'true'
  }),

  actions: {
    async fetchProviders() {
      this.loading = true
      try {
        const res = await api.get('/ai/providers')
        this.providers = res.data
      } catch (e: any) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async createProvider(provider: Partial<AIProvider>) {
      const res = await api.post('/ai/providers', provider)
      this.providers.push(res.data)
      return res.data
    },

    async updateProvider(id: number, provider: Partial<AIProvider>) {
      const res = await api.put(`/ai/providers/${id}`, provider)
      const idx = this.providers.findIndex(p => p.id === id)
      if (idx !== -1) {
        this.providers[idx] = res.data
      }
      return res.data
    },

    async deleteProvider(id: number) {
      await api.delete(`/ai/providers/${id}`)
      this.providers = this.providers.filter(p => p.id !== id)
    },

    async testConnection(provider: Partial<AIProvider>) {
      return await api.post('/ai/providers/test', {
        provider_type: provider.provider_type,
        base_url: provider.base_url,
        api_key: provider.api_key,
        model: provider.models?.[0] || 'default'
      })
    },

    async classifyTransaction(note: string, amount: number, date: string) {
      const res = await api.post('/ai/classify', null, {
        params: { note, amount, date }
      })
      return res.data
    },

    async fetchSuggestions(limit = 30) {
      const res = await api.get('/ai/suggestions', { params: { limit } })
      this.suggestions = res.data.suggestions
      return res.data.suggestions
    },

    setAutoClassify(enabled: boolean) {
      this.autoClassify = enabled
      localStorage.setItem('autoClassify', String(enabled))
    }
  }
})
```

---

### Task 8: Create AIProvidersView

**Files:**
- Create: `webui/src/views/AIProvidersView.vue`

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAIStore, type AIProvider } from '@/stores/ai'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import Modal from '@/components/ui/Modal.vue'

const aiStore = useAIStore()
const showModal = ref(false)
const editingProvider = ref<AIProvider | null>(null)
const testing = ref<number | null>(null)
const testResult = ref<{ success: boolean; message: string } | null>(null)

const providerTypes = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'ollama', label: 'Ollama (Local)' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google Gemini' },
  { value: 'azure', label: 'Azure OpenAI' },
  { value: 'mistral', label: 'Mistral' },
  { value: 'cohere', label: 'Cohere' },
  { value: 'together', label: 'Together AI' },
  { value: 'localai', label: 'LocalAI' },
  { value: 'llamafile', label: 'llamafile' },
  { value: 'jan', label: 'Jan.ai' }
]

const form = ref({
  name: '',
  provider_type: 'openai',
  base_url: '',
  api_key: '',
  models: '',
  is_active: true,
  priority: 100
})

onMounted(() => {
  aiStore.fetchProviders()
})

function openAdd() {
  editingProvider.value = null
  form.value = {
    name: '',
    provider_type: 'openai',
    base_url: '',
    api_key: '',
    models: '',
    is_active: true,
    priority: 100
  }
  showModal.value = true
}

function openEdit(provider: AIProvider) {
  editingProvider.value = provider
  form.value = {
    name: provider.name,
    provider_type: provider.provider_type,
    base_url: provider.base_url,
    api_key: provider.api_key || '',
    models: provider.models.join(', '),
    is_active: provider.is_active,
    priority: provider.priority
  }
  showModal.value = true
}

async function save() {
  const data = {
    ...form.value,
    models: form.value.models.split(',').map(m => m.trim()).filter(Boolean)
  }
  
  if (editingProvider.value) {
    await aiStore.updateProvider(editingProvider.value.id, data)
  } else {
    await aiStore.createProvider(data)
  }
  showModal.value = false
}

async function testProvider(provider: AIProvider) {
  testing.value = provider.id
  testResult.value = null
  try {
    const res = await aiStore.testConnection(provider)
    testResult.value = res.data
  } catch (e: any) {
    testResult.value = { success: false, message: e.message }
  } finally {
    testing.value = null
  }
}

async function toggleActive(provider: AIProvider) {
  await aiStore.updateProvider(provider.id, { is_active: !provider.is_active })
}

async function deleteProvider(id: number) {
  if (confirm('Are you sure you want to delete this provider?')) {
    await aiStore.deleteProvider(id)
  }
}

function getProviderLabel(type: string) {
  return providerTypes.find(p => p.value === type)?.label || type
}
</script>

<template>
  <div class="ai-providers">
    <div class="header">
      <h2>AI Providers</h2>
      <Button @click="openAdd">Add Provider</Button>
    </div>

    <div v-if="aiStore.loading" class="loading">Loading...</div>
    
    <div v-else-if="aiStore.providers.length === 0" class="empty">
      No AI providers configured. Add one to get started.
    </div>

    <div v-else class="provider-list">
      <Card v-for="provider in aiStore.providers" :key="provider.id" class="provider-card">
        <div class="provider-info">
          <div class="provider-header">
            <h3>{{ provider.name }}</h3>
            <span 
              class="status" 
              :class="{ active: provider.is_active }"
            >
              {{ provider.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <p class="provider-type">{{ getProviderLabel(provider.provider_type) }}</p>
          <p class="provider-url">{{ provider.base_url }}</p>
          <p v-if="provider.models.length" class="provider-models">
            Models: {{ provider.models.join(', ') }}
          </p>
          <p class="provider-priority">Priority: {{ provider.priority }}</p>
        </div>
        
        <div class="provider-actions">
          <Button 
            size="sm" 
            variant="secondary"
            @click="toggleActive(provider)"
          >
            {{ provider.is_active ? 'Disable' : 'Enable' }}
          </Button>
          <Button 
            size="sm" 
            variant="secondary"
            @click="testProvider(provider)"
            :disabled="testing === provider.id"
          >
            {{ testing === provider.id ? 'Testing...' : 'Test' }}
          </Button>
          <Button size="sm" variant="secondary" @click="openEdit(provider)">
            Edit
          </Button>
          <Button size="sm" variant="danger" @click="deleteProvider(provider.id)">
            Delete
          </Button>
        </div>

        <div v-if="testResult" class="test-result" :class="{ success: testResult.success, error: !testResult.success }">
          {{ testResult.message }}
        </div>
      </Card>
    </div>

    <!-- Modal -->
    <Modal v-model="showModal" :title="editingProvider ? 'Edit Provider' : 'Add Provider'">
      <form @submit.prevent="save" class="provider-form">
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" required />
        </div>
        
        <div class="form-group">
          <label>Provider Type</label>
          <select v-model="form.provider_type" required>
            <option v-for="p in providerTypes" :key="p.value" :value="p.value">
              {{ p.label }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Base URL</label>
          <input v-model="form.base_url" placeholder="https://api.openai.com/v1" required />
        </div>
        
        <div class="form-group">
          <label>API Key</label>
          <input v-model="form.api_key" type="password" placeholder="sk-..." />
        </div>
        
        <div class="form-group">
          <label>Models (comma-separated)</label>
          <input v-model="form.models" placeholder="gpt-4, gpt-3.5-turbo" />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Priority (lower = higher)</label>
            <input v-model.number="form.priority" type="number" min="1" />
          </div>
          
          <div class="form-group checkbox">
            <label>
              <input v-model="form.is_active" type="checkbox" />
              Active
            </label>
          </div>
        </div>
        
        <div class="form-actions">
          <Button type="button" variant="secondary" @click="showModal = false">Cancel</Button>
          <Button type="submit">Save</Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<style scoped>
.ai-providers {
  padding: var(--space-4);
  max-width: 800px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.header h2 {
  margin: 0;
}

.loading, .empty {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-secondary);
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.provider-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.provider-info {
  flex: 1;
}

.provider-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.provider-header h3 {
  margin: 0;
}

.status {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-tertiary);
}

.status.active {
  background: var(--color-success);
  color: white;
}

.provider-type {
  margin: var(--space-1) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.provider-url {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.provider-models {
  margin: var(--space-1) 0;
  font-size: var(--font-size-sm);
}

.provider-priority {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.provider-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.test-result {
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
}

.test-result.success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.test-result.error {
  background: var(--color-error-light);
  color: var(--color-error);
}

.provider-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.form-group input,
.form-group select {
  padding: var(--space-2);
  border: 1px solid var(--color-separator-opaque);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
}

.form-row {
  display: flex;
  gap: var(--space-4);
}

.form-row .form-group {
  flex: 1;
}

.form-group.checkbox {
  flex-direction: row;
  align-items: center;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
</style>
```

---

### Task 9: Create SmartCategoryToggle Component

**Files:**
- Create: `webui/src/components/ai/SmartCategoryToggle.vue`

```vue
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAIStore } from '@/stores/ai'
import Button from '@/components/ui/Button.vue'

const props = defineProps<{
  enabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:enabled', value: boolean): void
  (e: 'classify', note: string, amount: number, date: string): void
}>()

const aiStore = useAIStore()
const classifying = ref(false)
const suggestion = ref<{ category: string; confidence: number } | null>(null)

const localEnabled = ref(props.enabled ?? aiStore.autoClassify)

watch(() => props.enabled, (v) => {
  localEnabled.value = v ?? aiStore.autoClassify
})

function toggle() {
  localEnabled.value = !localEnabled.value
  aiStore.setAutoClassify(localEnabled.value)
  emit('update:enabled', localEnabled.value)
}

async function handleClassify(note: string, amount: number, date: string) {
  if (!localEnabled.value) return
  
  classifying.value = true
  try {
    const result = await aiStore.classifyTransaction(note, amount, date)
    suggestion.value = result
    emit('classify', note, amount, date)
  } catch (e) {
    console.error('Classification failed:', e)
  } finally {
    classifying.value = false
  }
}

defineExpose({ classify: handleClassify })
</script>

<template>
  <div class="smart-category-toggle">
    <label class="toggle-label">
      <input 
        type="checkbox" 
        :checked="localEnabled" 
        @change="toggle" 
      />
      <span class="toggle-switch"></span>
      <span class="toggle-text">
        AI Auto-Classify
        <span v-if="classifying" class="classifying">Classifying...</span>
      </span>
    </label>
    
    <div v-if="suggestion && suggestion.category" class="suggestion">
      <span class="suggestion-label">Suggested:</span>
      <span class="suggestion-category">{{ suggestion.category }}</span>
      <span class="confidence">({{ Math.round(suggestion.confidence * 100) }}%)</span>
    </div>
  </div>
</template>

<style scoped>
.smart-category-toggle {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.toggle-label input {
  display: none;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: var(--color-bg-tertiary);
  border-radius: 12px;
  position: relative;
  transition: background var(--duration-fast);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform var(--duration-fast);
  box-shadow: var(--shadow-sm);
}

.toggle-label input:checked + .toggle-switch {
  background: var(--color-primary);
}

.toggle-label input:checked + .toggle-switch::after {
  transform: translateX(20px);
}

.toggle-text {
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.classifying {
  color: var(--color-primary);
  font-size: var(--font-size-xs);
}

.suggestion {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-sm);
  padding: var(--space-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
}

.suggestion-label {
  color: var(--color-text-secondary);
}

.suggestion-category {
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
}

.confidence {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}
</style>
```

---

### Task 10: Create AISuggestionCard Component

**Files:**
- Create: `webui/src/components/ai/AISuggestionCard.vue`

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAIStore } from '@/stores/ai'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'

const aiStore = useAIStore()
const loading = ref(false)

onMounted(() => {
  if (aiStore.suggestions.length === 0) {
    refresh()
  }
})

async function refresh() {
  loading.value = true
  try {
    await aiStore.fetchSuggestions()
  } catch (e) {
    console.error('Failed to fetch suggestions:', e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="ai-suggestion-card">
    <div class="card-header">
      <h3>AI Insights</h3>
      <Button 
        size="sm" 
        variant="secondary"
        @click="refresh"
        :disabled="loading"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </Button>
    </div>
    
    <div v-if="aiStore.suggestions.length === 0" class="empty">
      <p>No suggestions yet. Add more transactions to get AI insights.</p>
    </div>
    
    <ul v-else class="suggestions-list">
      <li v-for="(suggestion, idx) in aiStore.suggestions" :key="idx">
        {{ suggestion }}
      </li>
    </ul>
  </Card>
</template>

<style scoped>
.ai-suggestion-card {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-bg-secondary) 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.card-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
}

.empty {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  text-align: center;
  padding: var(--space-4);
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.suggestions-list li {
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-primary);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  border-left: 3px solid var(--color-primary);
}
</style>
```

---

### Task 11: Update Settings View to Include AI Providers Link

**Files:**
- Modify: `webui/src/views/SettingsView.vue`

Add navigation to AI Providers in the settings page.

---

### Task 12: Update Router

**Files:**
- Modify: `webui/src/router/index.ts` (or main.ts)

Add route for AI Providers view.

---

## Testing

### Test Backend

```bash
# Start backend
cd /Users/liukunup/Documents/repo/money
python -m uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/ai/providers
curl -X POST http://localhost:8000/api/ai/providers/test \
  -H "Content-Type: application/json" \
  -d '{"provider_type":"openai","base_url":"https://api.openai.com/v1","api_key":"sk-test","model":"gpt-4"}'
```

### Test Frontend

```bash
cd webui
npm run dev
```

---

## Completion Criteria

1. Backend:
   - [ ] AIProvider model created
   - [ ] AIService with fallback implemented
   - [ ] All API routes working
   - [ ] Can add/edit/delete providers
   - [ ] Can test connection
   - [ ] Can classify transactions
   - [ ] Can get suggestions

2. Frontend:
   - [ ] AIProvidersView shows providers
   - [ ] Can add/edit/delete providers
   - [ ] SmartCategoryToggle works
   - [ ] AISuggestionCard shows on dashboard

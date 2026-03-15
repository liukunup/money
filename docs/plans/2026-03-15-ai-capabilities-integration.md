# AI Capabilities Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement Phase 4 AI capabilities for Money app with multi-provider support, fallback strategy, and keyword-based classification.

**Architecture:**
- Backend: Add AIProvider model, AIService with unified OpenAI-compatible interface, keyword-based classifier
- Frontend: Add AIProvidersView, SmartCategoryToggle component, AISuggestionCard component
- Fallback: Priority-based provider selection with automatic failover; keyword-based classification as ultimate fallback

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, httpx, Vue 3, TypeScript, Pinia

---

### Task 1: Create AIProvider Model

**Files:**
- Create: `app/models/ai_provider.py`
- Modify: `app/models/__init__.py`

**Step 1: Write the failing test**

```python
# tests/models/test_ai_provider.py
import pytest
from app.models.ai_provider import AIProvider

def test_ai_provider_creation():
    provider = AIProvider(
        name="OpenAI",
        provider_type="openai",
        base_url="https://api.openai.com/v1",
        api_key="sk-test",
        models=["gpt-4", "gpt-3.5-turbo"],
        is_active=True,
        priority=1
    )
    assert provider.name == "OpenAI"
    assert provider.provider_type == "openai"
    assert provider.is_active == True
    assert provider.priority == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/models/test_ai_provider.py -v`
Expected: FAIL with "No module named 'app.models.ai_provider'"

**Step 3: Write the implementation**

```python
# app/models/ai_provider.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class AIProvider(Base):
    """AI Provider Model"""
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider_type = Column(String(50), nullable=False)  # openai, deepseek, ollama, etc.
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(500), nullable=True)  # Optional for local providers
    models = Column(JSON, default=list)  # List of model names
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=100, nullable=False)  # Lower = higher priority
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Step 4: Update models/__init__.py**

```python
# app/models/__init__.py
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget, BudgetAlert
from app.models.ai_provider import AIProvider

__all__ = ["User", "Category", "Transaction", "Budget", "BudgetAlert", "AIProvider"]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/models/test_ai_provider.py -v`
Expected: PASS

---

### Task 2: Create AIProvider Schema

**Files:**
- Create: `app/schemas/ai_provider.py`

**Step 1: Write the schema**

```python
# app/schemas/ai_provider.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class AIProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    provider_type: str = Field(..., min_length=1, max_length=50)
    base_url: str = Field(..., min_length=1, max_length=255)
    api_key: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    is_active: bool = True
    priority: int = Field(default=100, ge=1, le=1000)

class AIProviderCreate(AIProviderBase):
    pass

class AIProviderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider_type: Optional[str] = Field(None, min_length=1, max_length=50)
    base_url: Optional[str] = Field(None, min_length=1, max_length=255)
    api_key: Optional[str] = None
    models: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)

class AIProviderResponse(AIProviderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AIProviderTestResult(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[float] = None
    models: Optional[List[str]] = None
```

---

### Task 3: Create AI Providers Admin API

**Files:**
- Create: `app/api/ai_providers.py`

**Step 1: Write the API endpoints**

```python
# app/api/ai_providers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import time
from app.db.database import get_db
from app.models.ai_provider import AIProvider
from app.schemas.ai_provider import (
    AIProviderCreate, 
    AIProviderUpdate, 
    AIProviderResponse,
    AIProviderTestResult
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

PROVIDER_TYPE_MAP = {
    "openai": {"default_url": "https://api.openai.com/v1", "needs_key": True},
    "deepseek": {"default_url": "https://api.deepseek.com/v1", "needs_key": True},
    "ollama": {"default_url": "http://localhost:11434", "needs_key": False},
    "anthropic": {"default_url": "https://api.anthropic.com/v1", "needs_key": True},
    "google": {"default_url": "https://generativelanguage.googleapis.com/v1", "needs_key": True},
    "mistral": {"default_url": "https://api.mistral.ai/v1", "needs_key": True},
    "cohere": {"default_url": "https://api.cohere.ai/v1", "needs_key": True},
    "moonshot": {"default_url": "https://api.moonshot.cn/v1", "needs_key": True},
    "ernie": {"default_url": "https://qianfan.baidubce.com/v2", "needs_key": True},
    "lmstudio": {"default_url": "http://localhost:1234/v1", "needs_key": False},
    "localai": {"default_url": "http://localhost:8080/v1", "needs_key": False},
    "hunyuan": {"default_url": "https://hunyuan.baidu.com/openapi/v2", "needs_key": True},
}

@router.get("/", response_model=List[AIProviderResponse])
def get_providers(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all AI providers"""
    query = db.query(AIProvider)
    if not include_inactive:
        query = query.filter(AIProvider.is_active == True)
    providers = query.order_by(AIProvider.priority).all()
    return providers

@router.post("/", response_model=AIProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(
    provider: AIProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new AI provider"""
    # Validate provider_type
    if provider.provider_type not in PROVIDER_TYPE_MAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider_type. Supported: {list(PROVIDER_TYPE_MAP.keys())}"
        )
    
    # Set default URL if not provided
    if not provider.base_url:
        provider.base_url = PROVIDER_TYPE_MAP[provider.provider_type]["default_url"]
    
    db_provider = AIProvider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.get("/{provider_id}", response_model=AIProviderResponse)
def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single AI provider"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.put("/{provider_id}", response_model=AIProviderResponse)
def update_provider(
    provider_id: int,
    provider: AIProviderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an AI provider"""
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db.delete(db_provider)
    db.commit()
    return None

@router.post("/{provider_id}/test", response_model=AIProviderTestResult)
async def test_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test AI provider connection"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    start_time = time.time()
    
    try:
        # Test connection with OpenAI-compatible /models endpoint
        headers = {}
        if provider.api_key:
            headers["Authorization"] = f"Bearer {provider.api_key}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{provider.base_url.rstrip('/')}/models",
                headers=headers
            )
            
        latency_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            models_data = response.json()
            models = []
            if "data" in models_data:
                models = [m.get("id", m.get("name", "")) for m in models_data["data"]]
            
            return AIProviderTestResult(
                success=True,
                message="Connection successful",
                latency_ms=round(latency_ms, 2),
                models=models
            )
        else:
            return AIProviderTestResult(
                success=False,
                message=f"HTTP {response.status_code}: {response.text[:100]}"
            )
            
    except httpx.ConnectError:
        return AIProviderTestResult(
            success=False,
            message="Connection failed: Unable to connect to provider"
        )
    except Exception as e:
        return AIProviderTestResult(
            success=False,
            message=f"Error: {str(e)[:100]}"
        )

@router.get("/types/list")
def get_provider_types():
    """Get list of supported provider types"""
    return [
        {"type": k, **v} for k, v in PROVIDER_TYPE_MAP.items()
    ]
```

---

### Task 4: Create AIService with OpenAI-compatible interface

**Files:**
- Create: `app/services/ai_service.py`

**Step 1: Write the service**

```python
# app/services/ai_service.py
from typing import Optional, List, Dict, Any
import httpx
import json
import logging
from app.models.ai_provider import AIProvider
from app.models.category import Category

logger = logging.getLogger(__name__)

class AIService:
    """Unified AI service with OpenAI-compatible interface and fallback"""
    
    def __init__(self, providers: List[AIProvider]):
        # Sort by priority (lower = higher priority)
        self.providers = sorted(providers, key=lambda p: p.priority)
        self.current_provider = None
        
    async def _call_provider(
        self, 
        provider: AIProvider, 
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Call a single AI provider"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if provider.api_key:
            headers["Authorization"] = f"Bearer {provider.api_key}"
        
        # Use first model if not specified
        selected_model = model or (provider.models[0] if provider.models else "gpt-3.5-turbo")
        
        payload = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{provider.base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload
            )
            
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    async def chat(
        self, 
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Call AI with fallback strategy"""
        last_error = None
        
        for provider in self.providers:
            try:
                result = await self._call_provider(
                    provider, messages, model, temperature
                )
                self.current_provider = provider.name
                # Extract content from OpenAI-compatible response
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return json.dumps(result)
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                last_error = e
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    async def classify_transaction(
        self,
        amount: float,
        transaction_type: str,  # 'income' or 'expense'
        note: str,
        categories: List[Category]
    ) -> Dict[str, Any]:
        """Classify a transaction using AI"""
        
        category_list = "\n".join([
            f"- {c.name} ({c.type})" for c in categories
        ])
        
        system_prompt = f"""You are a transaction classifier. 
Given a transaction with amount, type, and note, classify it into the most appropriate category.

Available categories:
{category_list}

Respond with ONLY a JSON object in this format:
{{
    "category_name": "category name here",
    "confidence": 0.95,
    "reasoning": "brief explanation"
}}

Do not include any other text."""

        user_message = f"""Classify this transaction:
- Amount: {amount}
- Type: {transaction_type}
- Note: {note}"""

        try:
            result = await self.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ])
            
            # Parse JSON response
            parsed = json.loads(result)
            return parsed
            
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            # Fall back to keyword-based classification
            return await self._keyword_classify(amount, transaction_type, note, categories)
    
    async def _keyword_classify(
        self,
        amount: float,
        transaction_type: str,
        note: str,
        categories: List[Category]
    ) -> Dict[str, Any]:
        """Keyword-based fallback classification"""
        
        # Keyword mappings
        keyword_map = {
            "餐饮": ["餐厅", "吃饭", "午餐", "晚餐", "早餐", "外卖", "麦当劳", "肯德基", "火锅", "烧烤", "日料", "披萨"],
            "交通": ["打车", "滴滴", "出租车", "地铁", "公交", "高铁", "火车", "飞机", "加油", "停车", "过路费"],
            "购物": ["淘宝", "京东", "拼多多", "天猫", "亚马逊", "快递", "网购"],
            "娱乐": ["电影", "KTV", "游戏", "演唱会", "酒吧", "咖啡", "奶茶"],
            "住房": ["房租", "水电", "物业", "燃气", "宽带"],
            "医疗": ["药店", "医院", "门诊", "体检", "保险"],
            "教育": ["学费", "培训", "书籍", "文具", "课程"],
            "工资": ["工资", "薪资", "月薪", "奖金", "补贴"],
            "投资": ["股票", "基金", "理财", "利息", "分红"],
        }
        
        note_lower = note.lower()
        
        for cat in categories:
            keywords = keyword_map.get(cat.name, [])
            for kw in keywords:
                if kw.lower() in note_lower:
                    return {
                        "category_name": cat.name,
                        "confidence": 0.5,  # Lower confidence for keyword match
                        "reasoning": f"Keyword match: {kw}"
                    }
        
        # Default to first matching category type
        for cat in categories:
            if cat.type == transaction_type:
                return {
                    "category_name": cat.name,
                    "confidence": 0.3,
                    "reasoning": "Default classification (no keywords matched)"
                }
        
        return {
            "category_name": categories[0].name if categories else "其他",
            "confidence": 0.1,
            "reasoning": "Fallback to first category"
        }


async def get_ai_service(db) -> AIService:
    """Get AI service instance with active providers"""
    providers = db.query(AIProvider).filter(
        AIProvider.is_active == True
    ).order_by(AIProvider.priority).all()
    
    return AIService(providers)
```

---

### Task 5: Create AI Classification API

**Files:**
- Create: `app/api/ai.py`

**Step 1: Write the AI API**

```python
# app/api/ai.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.database import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.services.ai_service import get_ai_service, AIService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

class ClassifyRequest(BaseModel):
    amount: float
    type: str  # 'income' or 'expense'
    note: str
    category_ids: Optional[List[int]] = None  # Limit to specific categories

class ClassifyResponse(BaseModel):
    category_name: str
    confidence: float
    reasoning: str
    used_ai: bool

class SuggestionResponse(BaseModel):
    suggestions: List[dict]
    provider_used: Optional[str] = None

@router.post("/classify", response_model=ClassifyResponse)
async def classify_transaction(
    request: ClassifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Classify a transaction using AI with fallback"""
    
    # Get categories
    query = db.query(Category).filter(Category.is_deleted == False)
    if request.category_ids:
        query = query.filter(Category.id.in_(request.category_ids))
    categories = query.all()
    
    if not categories:
        raise HTTPException(
            status_code=400,
            detail="No categories available for classification"
        )
    
    # Get AI service
    ai_service = await get_ai_service(db)
    
    try:
        result = await ai_service.classify_transaction(
            amount=request.amount,
            transaction_type=request.type,
            note=request.note,
            categories=categories
        )
        
        # Find matching category
        matched_category = None
        for cat in categories:
            if cat.name == result.get("category_name"):
                matched_category = cat
                break
        
        if not matched_category:
            # Try partial match
            for cat in categories:
                if result.get("category_name", "").lower() in cat.name.lower():
                    matched_category = cat
                    break
        
        if not matched_category:
            # Use first category of correct type
            for cat in categories:
                if cat.type == request.type:
                    matched_category = cat
                    break
        
        return ClassifyResponse(
            category_name=matched_category.name if matched_category else categories[0].name,
            confidence=result.get("confidence", 0.0),
            reasoning=result.get("reasoning", ""),
            used_ai=True
        )
        
    except Exception as e:
        # Return error response
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )

@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestions for recent uncategorized transactions"""
    
    # Get recent transactions without category
    recent_transactions = db.query(Transaction).filter(
        Transaction.category_id.is_(None)
    ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    if not recent_transactions:
        return SuggestionResponse(suggestions=[])
    
    categories = db.query(Category).filter(Category.is_deleted == False).all()
    ai_service = await get_ai_service(db)
    
    suggestions = []
    for txn in recent_transactions:
        try:
            result = await ai_service.classify_transaction(
                amount=float(txn.amount),
                transaction_type=txn.type,
                note=txn.note or "",
                categories=categories
            )
            
            suggestions.append({
                "transaction_id": txn.id,
                "amount": txn.amount,
                "type": txn.type,
                "note": txn.note,
                "suggested_category": result.get("category_name"),
                "confidence": result.get("confidence"),
                "reasoning": result.get("reasoning")
            })
        except:
            continue
    
    return SuggestionResponse(
        suggestions=suggestions,
        provider_used=ai_service.current_provider
    )
```

---

### Task 6: Register AI APIs in main.py

**Files:**
- Modify: `app/main.py`

**Step 1: Add routers**

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import users, categories, transactions, budgets, tags, time_periods, recycle_bin, ai_providers, ai

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(time_periods.router, prefix="/api/time-periods", tags=["time-periods"])
app.include_router(recycle_bin.router, prefix="/api/recycle-bin", tags=["recycle-bin"])
app.include_router(ai_providers.router, prefix="/api/ai-providers", tags=["ai-providers"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/")
async def root():
    return {"message": "Money API", "version": settings.APP_VERSION}
```

---

### Task 7: Create Frontend AI Provider Types

**Files:**
- Modify: `webui/src/types/models.ts`

**Step 1: Add AI types**

```typescript
// Add to webui/src/types/models.ts

// AI Provider Types
export interface AIProvider {
  id: number;
  name: string;
  provider_type: string;
  base_url: string;
  api_key?: string;
  models: string[];
  is_active: boolean;
  priority: number;
  created_at: string;
  updated_at?: string;
}

export interface AIProviderCreate {
  name: string;
  provider_type: string;
  base_url?: string;
  api_key?: string;
  models?: string[];
  is_active?: boolean;
  priority?: number;
}

export interface AIProviderUpdate {
  name?: string;
  provider_type?: string;
  base_url?: string;
  api_key?: string;
  models?: string[];
  is_active?: boolean;
  priority?: number;
}

export interface AIProviderTestResult {
  success: boolean;
  message: string;
  latency_ms?: number;
  models?: string[];
}

export interface ProviderType {
  type: string;
  default_url: string;
  needs_key: boolean;
}

// AI Classification Types
export interface ClassificationRequest {
  amount: number;
  type: 'income' | 'expense';
  note: string;
  category_ids?: number[];
}

export interface ClassificationResult {
  category_name: string;
  confidence: number;
  reasoning: string;
  used_ai: boolean;
}

export interface AISuggestion {
  transaction_id: number;
  amount: string;
  type: 'income' | 'expense';
  note?: string;
  suggested_category: string;
  confidence: number;
  reasoning: string;
}
```

---

### Task 8: Create AI Service (Frontend)

**Files:**
- Create: `webui/src/services/ai.service.ts`

**Step 1: Write the service**

```typescript
// webui/src/services/ai.service.ts
import axios from './api';
import type { 
  AIProvider, 
  AIProviderCreate, 
  AIProviderUpdate,
  AIProviderTestResult,
  ProviderType,
  ClassificationRequest,
  ClassificationResult,
  AISuggestion
} from '@/types/models';

export const aiService = {
  // Provider Management
  async getProviders(includeInactive = false) {
    const params = new URLSearchParams();
    if (includeInactive) params.append('include_inactive', 'true');
    const response = await axios.get<AIProvider[]>(`/ai-providers/?${params}`);
    return response.data;
  },

  async getProvider(id: number) {
    const response = await axios.get<AIProvider>(`/ai-providers/${id}`);
    return response.data;
  },

  async createProvider(provider: AIProviderCreate) {
    const response = await axios.post<AIProvider>('/ai-providers/', provider);
    return response.data;
  },

  async updateProvider(id: number, provider: AIProviderUpdate) {
    const response = await axios.put<AIProvider>(`/ai-providers/${id}`, provider);
    return response.data;
  },

  async deleteProvider(id: number) {
    await axios.delete(`/ai-providers/${id}`);
  },

  async testProvider(id: number): Promise<AIProviderTestResult> {
    const response = await axios.post<AIProviderTestResult>(`/ai-providers/${id}/test`);
    return response.data;
  },

  async getProviderTypes() {
    const response = await axios.get<ProviderType[]>('/ai-providers/types/list');
    return response.data;
  },

  // Classification
  async classifyTransaction(request: ClassificationRequest) {
    const response = await axios.post<ClassificationResult>('/ai/classify', request);
    return response.data;
  },

  // Suggestions
  async getSuggestions() {
    const response = await axios.get<{ suggestions: AISuggestion[]; provider_used?: string }>('/ai/suggestions');
    return response.data;
  },
};
```

---

### Task 9: Create AI Store (Pinia)

**Files:**
- Create: `webui/src/stores/ai.ts`

**Step 1: Write the store**

```typescript
// webui/src/stores/ai.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { aiService } from '@/services/ai.service';
import type { 
  AIProvider, 
  AIProviderCreate, 
  AIProviderTestResult,
  ClassificationRequest,
  ClassificationResult,
  AISuggestion 
} from '@/types/models';

export const useAIStore = defineStore('ai', () => {
  const providers = ref<AIProvider[]>([]);
  const suggestions = ref<AISuggestion[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const providerUsed = ref<string | null>(null);
  const autoClassify = ref(false); // Smart Category Toggle state

  // Computed
  const activeProviders = computed(() => 
    providers.value.filter(p => p.is_active)
  );

  const hasActiveProvider = computed(() => 
    activeProviders.value.length > 0
  );

  // Actions
  async function fetchProviders() {
    loading.value = true;
    error.value = null;
    try {
      providers.value = await aiService.getProviders();
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch providers';
    } finally {
      loading.value = false;
    }
  }

  async function createProvider(provider: AIProviderCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newProvider = await aiService.createProvider(provider);
      providers.value.push(newProvider);
      return newProvider;
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create provider';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateProvider(id: number, provider: Partial<AIProvider>) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await aiService.updateProvider(id, provider);
      const index = providers.value.findIndex(p => p.id === id);
      if (index !== -1) {
        providers.value[index] = updated;
      }
      return updated;
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to update provider';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deleteProvider(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await aiService.deleteProvider(id);
      providers.value = providers.value.filter(p => p.id !== id);
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete provider';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function testProvider(id: number): Promise<AIProviderTestResult> {
    loading.value = true;
    error.value = null;
    try {
      return await aiService.testProvider(id);
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to test provider';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function classifyTransaction(request: ClassificationRequest): Promise<ClassificationResult> {
    try {
      return await aiService.classifyTransaction(request);
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Classification failed';
      throw e;
    }
  }

  async function fetchSuggestions() {
    loading.value = true;
    error.value = null;
    try {
      const result = await aiService.getSuggestions();
      suggestions.value = result.suggestions;
      providerUsed.value = result.provider_used || null;
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch suggestions';
    } finally {
      loading.value = false;
    }
  }

  function toggleAutoClassify() {
    autoClassify.value = !autoClassify.value;
    localStorage.setItem('ai_auto_classify', String(autoClassify.value));
  }

  function loadAutoClassify() {
    const stored = localStorage.getItem('ai_auto_classify');
    autoClassify.value = stored === 'true';
  }

  return {
    providers,
    suggestions,
    loading,
    error,
    providerUsed,
    autoClassify,
    activeProviders,
    hasActiveProvider,
    fetchProviders,
    createProvider,
    updateProvider,
    deleteProvider,
    testProvider,
    classifyTransaction,
    fetchSuggestions,
    toggleAutoClassify,
    loadAutoClassify,
  };
});
```

---

### Task 10: Create AIProvidersView

**Files:**
- Create: `webui/src/views/AIProvidersView.vue`

**Step 1: Write the view**

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAIStore } from '@/stores/ai';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';
import Input from '@/components/ui/Input.vue';
import type { AIProviderCreate, AIProviderTestResult } from '@/types/models';

const aiStore = useAIStore();
const authStore = useAuthStore();

const showFormModal = ref(false);
const showTestResult = ref(false);
const testResult = ref<AIProviderTestResult | null>(null);
const providerToEdit = ref<number | null>(null);

// Form state
const form = ref<AIProviderCreate>({
  name: '',
  provider_type: 'openai',
  base_url: '',
  api_key: '',
  models: [],
  is_active: true,
  priority: 100,
});

const providerTypes = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'ollama', label: 'Ollama (Local)' },
  { value: 'anthropic', label: 'Anthropic Claude' },
  { value: 'google', label: 'Google Gemini' },
  { value: 'mistral', label: 'Mistral AI' },
  { value: 'moonshot', label: 'Moonshot (月之暗面)' },
  { value: 'ernie', label: 'Baidu ERNIE' },
  { value: 'lmstudio', label: 'LM Studio' },
  { value: 'localai', label: 'LocalAI' },
  { value: 'hunyuan', label: 'Tencent Hunyuan' },
];

onMounted(() => {
  authStore.checkAuth();
  aiStore.fetchProviders();
});

const handleAdd = () => {
  form.value = {
    name: '',
    provider_type: 'openai',
    base_url: '',
    api_key: '',
    models: [],
    is_active: true,
    priority: 100,
  };
  providerToEdit.value = null;
  showFormModal.value = true;
};

const handleEdit = (provider: any) => {
  form.value = {
    name: provider.name,
    provider_type: provider.provider_type,
    base_url: provider.base_url,
    api_key: provider.api_key || '',
    models: provider.models || [],
    is_active: provider.is_active,
    priority: provider.priority,
  };
  providerToEdit.value = provider.id;
  showFormModal.value = true;
};

const handleSubmit = async () => {
  try {
    if (providerToEdit.value) {
      await aiStore.updateProvider(providerToEdit.value, form.value);
    } else {
      await aiStore.createProvider(form.value);
    }
    showFormModal.value = false;
  } catch (e) {
    console.error('Failed to save provider:', e);
  }
};

const handleTest = async (id: number) => {
  testResult.value = null;
  showTestResult.value = true;
  testResult.value = await aiStore.testProvider(id);
};

const handleDelete = async (id: number) => {
  if (confirm('Are you sure you want to delete this provider?')) {
    await aiStore.deleteProvider(id);
  }
};

const toggleActive = async (provider: any) => {
  await aiStore.updateProvider(provider.id, { is_active: !provider.is_active });
};
</script>

<template>
  <div class="ai-providers-view">
    <!-- Header -->
    <div class="header">
      <h1 class="header__title">AI Providers</h1>
      <Button variant="primary" size="medium" @click="handleAdd">
        Add Provider
      </Button>
    </div>

    <!-- Info Banner -->
    <div class="info-banner">
      <span class="info-icon">ℹ️</span>
      <span>Configure AI providers for automatic transaction classification. Lower priority = higher preference.</span>
    </div>

    <!-- Providers List -->
    <div class="providers-grid">
      <div
        v-for="provider in aiStore.providers"
        :key="provider.id"
        :class="['provider-card', { 'provider-card--inactive': !provider.is_active }]"
      >
        <div class="provider-header">
          <div class="provider-info">
            <h3 class="provider-name">{{ provider.name }}</h3>
            <span class="provider-type">{{ provider.provider_type }}</span>
          </div>
          <label class="toggle">
            <input 
              type="checkbox" 
              :checked="provider.is_active"
              @change="toggleActive(provider)"
            >
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="provider-details">
          <div class="detail-row">
            <span class="detail-label">URL:</span>
            <span class="detail-value">{{ provider.base_url }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Priority:</span>
            <span class="detail-value">{{ provider.priority }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Models:</span>
            <span class="detail-value">{{ provider.models?.join(', ') || 'N/A' }}</span>
          </div>
        </div>

        <div class="provider-actions">
          <Button variant="secondary" size="small" @click="handleTest(provider.id)">
            Test
          </Button>
          <Button variant="tertiary" size="small" @click="handleEdit(provider)">
            Edit
          </Button>
          <Button variant="destructive" size="small" @click="handleDelete(provider.id)">
            Delete
          </Button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!aiStore.loading && aiStore.providers.length === 0" class="empty-state">
      <div class="empty-icon">🤖</div>
      <p class="empty-text">No AI providers configured</p>
      <p class="empty-subtext">Add an AI provider to enable smart transaction classification</p>
    </div>

    <!-- Loading State -->
    <div v-if="aiStore.loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading providers...</p>
    </div>

    <!-- Form Modal -->
    <div v-if="showFormModal" class="modal-overlay" @click.self="showFormModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ providerToEdit ? 'Edit Provider' : 'Add Provider' }}</h2>
          <button class="modal-close" @click="showFormModal = false">×</button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-body">
          <Input v-model="form.name" label="Name" placeholder="My OpenAI" required />
          
          <div class="form-group">
            <label>Provider Type</label>
            <select v-model="form.provider_type" class="select-input">
              <option v-for="pt in providerTypes" :key="pt.value" :value="pt.value">
                {{ pt.label }}
              </option>
            </select>
          </div>

          <Input v-model="form.base_url" label="Base URL" placeholder="https://api.openai.com/v1" />
          
          <Input v-model="form.api_key" label="API Key" type="password" placeholder="sk-..." />
          
          <Input v-model="form.priority" label="Priority" type="number" placeholder="100" />

          <div class="form-group">
            <label>Models (comma-separated)</label>
            <input 
              v-model="form.models" 
              type="text" 
              placeholder="gpt-4, gpt-3.5-turbo"
              class="text-input"
            >
          </div>

          <div class="form-actions">
            <Button type="button" variant="tertiary" @click="showFormModal = false">
              Cancel
            </Button>
            <Button type="submit" variant="primary" :loading="aiStore.loading">
              {{ providerToEdit ? 'Update' : 'Create' }}
            </Button>
          </div>
        </form>
      </div>
    </div>

    <!-- Test Result Modal -->
    <div v-if="showTestResult" class="modal-overlay" @click.self="showTestResult = false">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Connection Test</h2>
          <button class="modal-close" @click="showTestResult = false">×</button>
        </div>
        
        <div class="modal-body">
          <div :class="['test-result', testResult?.success ? 'test-result--success' : 'test-result--error']">
            <div class="test-status">{{ testResult?.success ? '✓ Success' : '✗ Failed' }}</div>
            <p>{{ testResult?.message }}</p>
            <p v-if="testResult?.latency_ms">Latency: {{ testResult.latency_ms }}ms</p>
            <p v-if="testResult?.models?.length">Models: {{ testResult.models.join(', ') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-providers-view {
  min-height: 100vh;
  background: var(--color-bg-secondary);
  padding: var(--space-4);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
}

.header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.info-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.providers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
}

.provider-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.provider-card--inactive {
  opacity: 0.6;
}

.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}

.provider-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.provider-type {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.provider-details {
  margin-bottom: var(--space-3);
}

.detail-row {
  display: flex;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-1);
}

.detail-label {
  color: var(--color-text-secondary);
  min-width: 70px;
}

.detail-value {
  color: var(--color-text-primary);
  word-break: break-all;
}

.provider-actions {
  display: flex;
  gap: var(--space-2);
}

/* Toggle */
.toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-bg-tertiary);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle input:checked + .toggle-slider {
  background-color: var(--color-primary);
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-separator);
}

.modal-header h2 {
  margin: 0;
  font-size: var(--font-size-xl);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.modal-body {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.select-input, .text-input {
  padding: var(--space-3);
  border: 1px solid var(--color-separator);
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.form-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
  margin-top: var(--space-4);
}

.test-result {
  padding: var(--space-4);
  border-radius: var(--radius-md);
}

.test-result--success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid #22c55e;
}

.test-result--error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
}

.test-status {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-2);
}

.empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
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
  to { transform: rotate(360deg); }
}
</style>
```

---

### Task 11: Create SmartCategoryToggle Component

**Files:**
- Create: `webui/src/components/ai/SmartCategoryToggle.vue`

**Step 1: Write the component**

```vue
<script setup lang="ts">
import { onMounted } from 'vue';
import { useAIStore } from '@/stores/ai';

const aiStore = useAIStore();

onMounted(() => {
  aiStore.loadAutoClassify();
});

const handleToggle = () => {
  aiStore.toggleAutoClassify();
};
</script>

<template>
  <div class="smart-toggle" @click="handleToggle">
    <div class="smart-toggle__icon">🤖</div>
    <div class="smart-toggle__content">
      <span class="smart-toggle__label">Smart Category</span>
      <span class="smart-toggle__desc">Auto-classify with AI</span>
    </div>
    <label class="toggle">
      <input type="checkbox" :checked="aiStore.autoClassify">
      <span class="toggle-slider"></span>
    </label>
  </div>
</template>

<style scoped>
.smart-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.smart-toggle:hover {
  background: var(--color-bg-tertiary);
}

.smart-toggle__icon {
  font-size: 24px;
}

.smart-toggle__content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.smart-toggle__label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.smart-toggle__desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-bg-tertiary);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle input:checked + .toggle-slider {
  background-color: var(--color-primary);
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(20px);
}
</style>
```

---

### Task 12: Create AISuggestionCard Component

**Files:**
- Create: `webui/src/components/ai/AISuggestionCard.vue`

**Step 1: Write the component**

```vue
<script setup lang="ts">
import { computed } from 'vue';
import type { AISuggestion } from '@/types/models';

const props = defineProps<{
  suggestion: AISuggestion;
}>();

const emit = defineEmits<{
  (e: 'apply', suggestion: AISuggestion): void;
  (e: 'dismiss', transactionId: number): void;
}>();

const confidenceClass = computed(() => {
  if (props.suggestion.confidence >= 0.8) return 'high';
  if (props.suggestion.confidence >= 0.5) return 'medium';
  return 'low';
});

const formatAmount = (amount: string) => {
  const num = parseFloat(amount);
  return num.toLocaleString('zh-CN', { style: 'currency', currency: 'CNY' });
};
</script>

<template>
  <div class="suggestion-card">
    <div class="suggestion-header">
      <span class="suggestion-amount">{{ formatAmount(suggestion.amount) }}</span>
      <span :class="['suggestion-type', suggestion.type]">
        {{ suggestion.type === 'income' ? 'Income' : 'Expense' }}
      </span>
    </div>
    
    <div class="suggestion-note" v-if="suggestion.note">
      {{ suggestion.note }}
    </div>
    
    <div class="suggestion-content">
      <div class="suggestion-category">
        <span class="category-label">Suggested:</span>
        <span class="category-name">{{ suggestion.suggested_category }}</span>
      </div>
      
      <div class="suggestion-confidence">
        <span class="confidence-label">Confidence:</span>
        <div class="confidence-bar">
          <div 
            class="confidence-fill" 
            :class="confidenceClass"
            :style="{ width: `${suggestion.confidence * 100}%` }"
          ></div>
        </div>
        <span class="confidence-value">{{ Math.round(suggestion.confidence * 100) }}%</span>
      </div>
      
      <div class="suggestion-reasoning" v-if="suggestion.reasoning">
        {{ suggestion.reasoning }}
      </div>
    </div>
    
    <div class="suggestion-actions">
      <button class="btn-dismiss" @click="emit('dismiss', suggestion.transaction_id)">
        Dismiss
      </button>
      <button class="btn-apply" @click="emit('apply', suggestion)">
        Apply
      </button>
    </div>
  </div>
</template>

<style scoped>
.suggestion-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.suggestion-amount {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

.suggestion-type {
  font-size: var(--font-size-xs);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  text-transform: uppercase;
}

.suggestion-type.income {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.suggestion-type.expense {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.suggestion-note {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
}

.suggestion-content {
  margin-bottom: var(--space-3);
}

.suggestion-category {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.category-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.category-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
}

.suggestion-confidence {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.confidence-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.confidence-bar {
  flex: 1;
  height: 6px;
  background: var(--color-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: 3px;
  transition: width var(--duration-normal);
}

.confidence-fill.high {
  background: #22c55e;
}

.confidence-fill.medium {
  background: #eab308;
}

.confidence-fill.low {
  background: #ef4444;
}

.confidence-value {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  min-width: 35px;
}

.suggestion-reasoning {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-style: italic;
}

.suggestion-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}

.btn-dismiss, .btn-apply {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.btn-dismiss {
  background: none;
  border: 1px solid var(--color-separator);
  color: var(--color-text-secondary);
}

.btn-dismiss:hover {
  background: var(--color-bg-tertiary);
}

.btn-apply {
  background: var(--color-primary);
  border: none;
  color: white;
}

.btn-apply:hover {
  opacity: 0.9;
}
</style>
```

---

### Task 13: Update Router

**Files:**
- Modify: `webui/src/router/index.ts`

**Step 1: Add route**

```typescript
// Add import
import AIProvidersView from '@/views/AIProvidersView.vue';

// Add route
{
  path: '/ai-providers',
  name: 'ai-providers',
  component: AIProvidersView,
  meta: { requiresAuth: true }
},
```

---

### Task 14: Update SettingsView with AI Settings

**Files:**
- Modify: `webui/src/views/SettingsView.vue`

**Step 1: Add AI settings section**

```vue
<!-- Add to SettingsView.vue template -->
<div class="settings-section">
  <h2 class="settings-section__title">AI Settings</h2>
  <div class="settings-card">
    <div class="settings-row">
      <div class="settings-row__content">
        <span class="settings-row__label">Smart Classification</span>
        <span class="settings-row__desc">Automatically categorize transactions using AI</span>
      </div>
      <SmartCategoryToggle />
    </div>
    <div class="settings-row">
      <div class="settings-row__content">
        <span class="settings-row__label">Manage Providers</span>
        <span class="settings-row__desc">Configure AI provider settings</span>
      </div>
      <Button variant="secondary" @click="router.push('/ai-providers')">
        Configure
      </Button>
    </div>
  </div>
</div>

<!-- Add import -->
import SmartCategoryToggle from '@/components/ai/SmartCategoryToggle.vue';
import { useRouter } from 'vue-router';

const router = useRouter();
```

---

### Task 15: Update DashboardView with AISuggestionCard

**Files:**
- Modify: `webui/src/views/DashboardView.vue`

**Step 1: Add suggestions section**

```vue
<!-- Add script imports -->
import AISuggestionCard from '@/components/ai/AISuggestionCard.vue';
import { useAIStore } from '@/stores/ai';
import { useTransactionsStore } from '@/stores/transactions';

const aiStore = useAIStore();
const transactionsStore = useTransactionsStore();

// Add onMounted
onMounted(async () => {
  // ... existing code
  if (aiStore.hasActiveProvider) {
    await aiStore.fetchSuggestions();
  }
});

// Add applySuggestion function
const applySuggestion = async (suggestion: any) => {
  // Find the category
  const category = categoriesStore.categories.find(
    c => c.name === suggestion.suggested_category
  );
  if (category) {
    await transactionsStore.updateTransaction(suggestion.transaction_id, {
      category_id: category.id
    });
    // Remove from suggestions
    aiStore.suggestions = aiStore.suggestions.filter(
      s => s.transaction_id !== suggestion.transaction_id
    );
  }
};

const dismissSuggestion = (transactionId: number) => {
  aiStore.suggestions = aiStore.suggestions.filter(
    s => s.transaction_id !== transactionId
  );
};
```

```vue
<!-- Add to template -->
<div v-if="aiStore.hasActiveProvider && aiStore.suggestions.length > 0" class="suggestions-section">
  <h2 class="section-title">AI Suggestions</h2>
  <div class="suggestions-list">
    <AISuggestionCard
      v-for="suggestion in aiStore.suggestions"
      :key="suggestion.transaction_id"
      :suggestion="suggestion"
      @apply="applySuggestion"
      @dismiss="dismissSuggestion"
    />
  </div>
</div>
```

---

### Task 16: Database Migration

**Files:**
- Create: Run SQL or use Alembic

**Step 1: Add table to database**

```bash
# Using SQLite directly (or create migration)
python -c "
from app.db.database import engine, Base
from app.models.ai_provider import AIProvider

Base.metadata.create_all(bind=engine)
print('AIProvider table created')
"
```

---

### Task 17: Test Full Integration

**Step 1: Test backend**

```bash
# Start server
python -m uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/ai-providers/types/list
curl http://localhost:8000/api/ai-providers/ -H "Authorization: Bearer <token>"
```

**Step 2: Test frontend**

```bash
cd webui
npm run dev
```

**Step 3: Verify features**
- Add an AI provider (e.g., Ollama for local testing)
- Test connection
- Toggle smart category
- View AI suggestions on dashboard

---

## Execution

**Plan complete and saved to `docs/plans/2026-03-15-ai-capabilities-integration.md`.**

Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?

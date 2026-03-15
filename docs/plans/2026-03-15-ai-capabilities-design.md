# Phase 4: AI Capabilities Integration Design

## Overview

Implement AI-powered features for the Money app including:
- AI Provider management (multiple OpenAI-compatible providers)
- Transaction classification using AI
- Spending suggestions

## Backend Design

### 1. AIProvider Model

```python
class AIProvider(Base):
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)          # "DeepSeek", "Ollama Local"
    provider_type = Column(String(20), nullable=False)  # "openai", "anthropic", "google"
    base_url = Column(String(255), nullable=False)     # API endpoint URL
    api_key = Column(String(255))                      # API key (stored as-is for simplicity)
    models = Column(JSON, default=list)               # ["deepseek-chat", "llama3"]
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=100)            # Lower = higher priority
    created_at = Column(DateTime, server_default=func.now())
```

### 2. Supported Provider Types

| Type | Display Name | Notes |
|------|--------------|-------|
| openai | OpenAI | GPT models |
| deepseek | DeepSeek | Cheap alternative |
| ollama | Ollama | Local, free |
| anthropic | Anthropic | Claude models |
| google | Google | Gemini models |
| azure | Azure OpenAI | Enterprise |
| mistral | Mistral | Mistral AI |
| cohere | Cohere | Cohere |
| together | Together AI | Aggregator |
| localai | LocalAI | Self-hosted |
| llamafile | llamafile | Local |
| jan | Jan | Local |

### 3. AIService

**Interface:**
```python
class AIService:
    async def chat(messages: list[dict], model: str = None) -> str
    async def classify_transaction(note: str, amount: float, categories: list) -> dict
    async def get_suggestions(transactions: list) -> list[str]
```

**Fallback Strategy:**
1. Query active providers ordered by priority ASC
2. Try first provider, capture exception
3. On failure → try next provider in list
4. Return error only if ALL providers fail

### 4. API Endpoints

#### Admin API (Provider Management)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ai/providers` | List all providers |
| POST | `/api/ai/providers` | Create provider |
| PUT | `/api/ai/providers/{id}` | Update provider |
| DELETE | `/api/ai/providers/{id}` | Delete provider |
| POST | `/api/ai/providers/test` | Test connection |

#### AI API (User-facing)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ai/classify` | Classify transaction |
| GET | `/api/ai/suggestions` | Get AI suggestions |

### 5. Classification Prompt

```
You are a financial category classifier for personal expenses.
Available categories: 餐饮, 交通, 购物, 娱乐, 住房, 医疗, 教育, 工资, 奖金, 投资, 其他

Classify this transaction:
- Amount: {amount}
- Note: {note}
- Date: {date}

Respond with ONLY valid JSON (no other text):
{{"category": "餐饮", "confidence": 0.95}}
```

## Frontend Design

### 1. AIProvidersView

- Located in Settings section
- List all AI providers with status (active/inactive)
- Add provider modal form
- Edit provider modal form
- Test connection button
- Delete confirmation

### 2. SmartCategoryToggle

- Toggle component in transaction form
- When ON: auto-classify transactions using AI
- When OFF: manual category selection
- Saves preference to localStorage

### 3. AISuggestionCard

- Dashboard card showing AI-generated insights
- Example: "Your dining expenses increased by 20% this month"
- Refresh button to get new suggestions

## Security Considerations

- API keys stored in plain text (per requirements, could be encrypted)
- All AI endpoints require authentication
- Provider management requires authentication (any logged-in user)

## Error Handling

- Connection test returns success/error with message
- Classification returns "other" category on failure
- Suggestions return empty list on failure

## Testing

- Test each provider type connection
- Test fallback when primary provider fails
- Test classification accuracy with various notes

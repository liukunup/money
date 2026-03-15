from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
import json


class AIProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    provider_type: str = Field(..., pattern="^(openai|anthropic|ollama|deepseek|azure|moonshot|zhipu|minimax|qianwen|tongyi|spark|hunyuan|other)$")
    base_url: str = Field(..., min_length=1, max_length=255)
    api_key: Optional[str] = None
    models: Optional[List[str]] = None
    is_active: bool = True
    priority: int = Field(default=100, ge=1, le=1000)


class AIProviderCreate(AIProviderBase):
    pass


class AIProviderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    provider_type: Optional[str] = Field(None, pattern="^(openai|anthropic|ollama|deepseek|azure|moonshot|zhipu|minimax|qianwen|tongyi|spark|hunyuan|other)$")
    base_url: Optional[str] = Field(None, min_length=1, max_length=255)
    api_key: Optional[str] = None
    models: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)


class AIProviderResponse(AIProviderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('models', mode='before')
    @classmethod
    def parse_models(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    model_config = ConfigDict(from_attributes=True)


# Supported providers constant
SUPPORTED_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "default_url": "https://api.openai.com/v1",
        "default_models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    },
    "anthropic": {
        "name": "Anthropic",
        "default_url": "https://api.anthropic.com/v1",
        "default_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    },
    "ollama": {
        "name": "Ollama",
        "default_url": "http://localhost:11434/v1",
        "default_models": ["llama2", "mistral", "codellama"]
    },
    "deepseek": {
        "name": "DeepSeek",
        "default_url": "https://api.deepseek.com/v1",
        "default_models": ["deepseek-chat", "deepseek-coder"]
    },
    "azure": {
        "name": "Azure OpenAI",
        "default_url": "https://{resource}.openai.azure.com/openai",
        "default_models": ["gpt-4", "gpt-35-turbo"]
    },
    "moonshot": {
        "name": "Moonshot AI",
        "default_url": "https://api.moonshot.cn/v1",
        "default_models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
    },
    "zhipu": {
        "name": "Zhipu AI",
        "default_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_models": ["glm-4", "glm-3-turbo"]
    },
    "minimax": {
        "name": "MiniMax",
        "default_url": "https://api.minimax.chat/v1",
        "default_models": ["abab5.5-chat", "abab6-chat"]
    },
    "qianwen": {
        "name": "Qianwen (Alibaba)",
        "default_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_models": ["qwen-turbo", "qwen-plus", "qwen-max"]
    },
    "tongyi": {
        "name": "Tongyi (Alibaba)",
        "default_url": "https://dashscope.aliyuncs.com/api/v1",
        "default_models": ["qwen-vl-plus", "qwen-audio"]
    },
    "spark": {
        "name": "iFlytek Spark",
        "default_url": "https://spark-api.xf-yun.com/v3.5",
        "default_models": ["generalv3.5"]
    },
    "hunyuan": {
        "name": "Tencent Hunyuan",
        "default_url": "https://hunyuan.cloud.tencent.com",
        "default_models": ["hunyuan-pro", "hunyuan-standard"]
    }
}

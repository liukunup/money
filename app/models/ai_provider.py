from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class AIProvider(Base):
    """AI Provider model - supports 10+ providers with OpenAI-compatible interface"""
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # e.g., "OpenAI", "DeepSeek", "Ollama"
    provider_type = Column(String(20), nullable=False)  # 'openai', 'anthropic', 'ollama', etc.
    base_url = Column(String(255), nullable=False)  # API base URL
    api_key = Column(Text, nullable=True)  # API key (encrypted in production)
    models = Column(Text, nullable=True)  # JSON string of available models
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=100, nullable=False)  # Lower = higher priority
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

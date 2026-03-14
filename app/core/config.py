from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "Money"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_TYPE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///./data/money.db"

    # 安全配置
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # CORS 配置
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

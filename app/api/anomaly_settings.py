# app/api/settings.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory settings (for MVP - could be stored in DB later)
class AnomalySettings(BaseModel):
    warning_threshold: float = 2.0
    anomaly_threshold: float = 3.0
    large_transaction_threshold: float = 10000.0

anomaly_settings = AnomalySettings()

@router.get("/settings/anomaly", response_model=AnomalySettings)
def get_anomaly_settings():
    """Get current anomaly detection settings."""
    return anomaly_settings

@router.put("/settings/anomaly", response_model=AnomalySettings)
def update_anomaly_settings(settings: AnomalySettings):
    """Update anomaly detection settings."""
    global anomaly_settings
    anomaly_settings = settings
    return anomaly_settings

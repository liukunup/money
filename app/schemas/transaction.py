from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class TransactionAnomalyInfo(BaseModel):
    """Anomaly detection information for a transaction."""
    anomaly_level: Optional[str] = Field(None, description="warning | anomaly | alert | None")
    category_monthly_average: Optional[Decimal] = Field(None, description="Monthly average for category")
    anomaly_reason: Optional[str] = Field(None, description="Human-readable reason")


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: str = Field(..., pattern="^(income|expense)$")
    category_id: int = Field(..., gt=0)
    date: date
    note: Optional[str] = None
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="List of tag IDs")

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[date] = None
    note: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    anomaly_info: Optional[TransactionAnomalyInfo] = None

    model_config = ConfigDict(from_attributes=True)

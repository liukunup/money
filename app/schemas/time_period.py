from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

class TimePeriodBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(custom|monthly|quarterly|yearly)?$")
    start_date: date
    end_date: date
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    description: Optional[str] = None

class TimePeriodCreate(TimePeriodBase):
    pass

class TimePeriodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(custom|monthly|quarterly|yearly)?$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    description: Optional[str] = None

class TimePeriodResponse(TimePeriodBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

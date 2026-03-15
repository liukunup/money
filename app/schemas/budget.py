from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category_id: Optional[int] = None  # null means overall budget
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    period_type: str = Field(..., pattern="^(weekly|monthly|yearly)$")
    start_date: date
    end_date: Optional[date] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    amount: Optional[Decimal] = None
    period_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[int] = None


class BudgetResponse(BudgetBase):
    id: int
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetWithUsage(BudgetResponse):
    """Budget with calculated usage"""
    spent: Decimal = Field(default=Decimal("0"))
    remaining: Decimal = Field(default=Decimal("0"))
    percent_used: float = Field(default=0.0)
    category_name: Optional[str] = None
    category_icon: Optional[str] = None


# Budget Alert Schemas
class AlertStatus(str):
    PENDING = "pending"
    TRIGGERED = "triggered"
    RESOLVED = "resolved"


class BudgetAlertBase(BaseModel):
    budget_id: int = Field(..., gt=0)
    threshold_percent: int = Field(..., ge=1, le=100)


class BudgetAlertCreate(BudgetAlertBase):
    pass


class BudgetAlertUpdate(BaseModel):
    status: Optional[str] = None
    threshold_percent: Optional[int] = None


class BudgetAlertResponse(BudgetAlertBase):
    id: int
    status: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Analytics Schemas
class BudgetUsageResponse(BaseModel):
    budget_id: int
    budget_name: str
    period_type: str
    start_date: date
    end_date: date
    amount: Decimal
    spent: Decimal
    remaining: Decimal
    percent_used: float
    is_over_budget: bool
    alerts_triggered: list[BudgetAlertResponse] = []


class OverallBudgetSummary(BaseModel):
    total_budgets: int
    active_budgets: int
    total_budget_amount: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    budgets: list[BudgetWithUsage]
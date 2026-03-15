from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class PeriodType(str, enum.Enum):
    """预算周期类型"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class AlertStatus(str, enum.Enum):
    """告警状态"""
    PENDING = "pending"
    TRIGGERED = "triggered"
    RESOLVED = "resolved"


class Budget(Base):
    """预算模型"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # null means overall budget
    amount = Column(Numeric(12, 2), nullable=False)
    period_type = Column(SQLEnum(PeriodType), nullable=False, default=PeriodType.MONTHLY)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # null means infinite
    is_active = Column(Integer, default=1, nullable=False)  # 1=active, 0=inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="budgets")
    alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete-orphan")


class BudgetAlert(Base):
    """预算告警模型"""
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    threshold_percent = Column(Integer, nullable=False)  # e.g., 80 means 80%
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.PENDING)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    budget = relationship("Budget", back_populates="alerts")
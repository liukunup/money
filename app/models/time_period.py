from sqlalchemy import Column, Integer, String, DateTime, Date, Text
from sqlalchemy.sql import func
from app.db.database import Base

class TimePeriod(Base):
    """时间段模型 - 用于定义特定的时间段进行分析"""
    __tablename__ = "time_periods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20))  # 'custom', 'monthly', 'quarterly', 'yearly'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    color = Column(String(7), default="#34C759")  # Hex color code
    icon = Column(String(20))  # Emoji or icon
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

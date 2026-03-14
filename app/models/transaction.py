from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base

class Transaction(Base):
    """交易模型（简化版，暂不加软删除和用户）"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' or 'expense'
    category_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

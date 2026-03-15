from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

# Transaction-Tag association table
transaction_tags = Table(
    'transaction_tags',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    type = Column(String(20))  # 'general', 'expense', 'income' - optional categorization
    color = Column(String(7), default="#007AFF")  # Hex color code
    icon = Column(String(20))  # Emoji or icon
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    transactions = relationship("Transaction", secondary=transaction_tags, back_populates="tags")

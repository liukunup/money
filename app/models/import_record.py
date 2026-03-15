from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class ImportRecord(Base):
    """导入记录模型"""
    __tablename__ = "import_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'alipay_csv', 'wechat_csv', 'excel'
    file_path = Column(Text, nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA256
    import_count = Column(Integer, default=0)
    status = Column(String(20), default='pending')  # 'pending', 'parsed', 'confirmed', 'failed'
    error_message = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="import_records")
    transactions = relationship("Transaction", back_populates="import_record")

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ImportRecordBase(BaseModel):
    file_name: str
    file_type: str
    file_path: str
    file_hash: str

class ImportRecordCreate(ImportRecordBase):
    pass

class ImportRecordUpdate(BaseModel):
    status: Optional[str] = None
    import_count: Optional[int] = None
    error_message: Optional[str] = None

class ImportRecordResponse(ImportRecordBase):
    id: int
    import_count: int
    status: str
    error_message: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ParsedTransactionSchema(BaseModel):
    """解析后的交易预览"""
    amount: Decimal
    type: str
    date: datetime
    note: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None


class ImportPreviewResponse(BaseModel):
    """导入预览响应"""
    import_id: int
    file_name: str
    total_count: int
    income_count: int
    expense_count: int
    transactions: List[ParsedTransactionSchema]


class ImportConfirmRequest(BaseModel):
    """确认导入请求"""
    import_id: int
    # 可选的分类映射，覆盖自动分类
    category_mapping: Optional[dict[int, int]] = Field(default_factory=dict)


class ImportConfirmResponse(BaseModel):
    """确认导入响应"""
    import_id: int
    created_count: int
    import_record: ImportRecordResponse

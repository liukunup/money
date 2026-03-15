# CSV/Excel Import Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement Phase 2: CSV/Excel Import for Alipay/WeChat bill import with auto-classification (keyword first, AI fallback) and storage support (local + MinIO).

**Architecture:** 
- Backend: FastAPI with SQLAlchemy, file storage abstraction (local filesystem + MinIO), CSV/Excel parsing with pandas/openpyxl
- Frontend: Vue 3 with drag-drop upload, preview table, import history list
- Auto-classification: Keyword matching against merchant names → category, with AI fallback

**Tech Stack:** FastAPI, SQLAlchemy 2.0, pandas, openpyxl, python-multipart, hashlib, Vue 3, Pinia

---

## Task 1: Backend - Config & Storage Infrastructure

**Files:**
- Modify: `app/core/config.py` - Add storage config (local path, MinIO settings)
- Create: `app/models/import_record.py` - ImportRecord model
- Create: `app/schemas/import_record.py` - ImportRecord schemas
- Create: `app/services/storage.py` - StorageBackend (local + MinIO)

**Step 1: Update config.py**

Add storage configuration:

```python
# Storage configuration
STORAGE_TYPE: str = "local"  # "local" or "minio"
STORAGE_LOCAL_PATH: str = "./data/imports"
STORAGE_MINIO_ENDPOINT: str = "localhost:9000"
STORAGE_MINIO_BUCKET: str = "money-imports"
STORAGE_MINIO_ACCESS_KEY: str = ""
STORAGE_MINIO_SECRET_KEY: str = ""
STORAGE_MINIO_SECURE: bool = False
```

**Step 2: Create ImportRecord model**

```python
# app/models/import_record.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class ImportStatus(str, enum.Enum):
    PENDING = "pending"
    PARSED = "parsed"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class ImportRecord(Base):
    """导入记录模型"""
    __tablename__ = "import_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # "csv", "xlsx"
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)  # SHA256
    import_count = Column(Integer, default=0)
    status = Column(Enum(ImportStatus), default=ImportStatus.PENDING)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    error_message = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Step 3: Create ImportRecord schemas**

```python
# app/schemas/import_record.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ImportRecordBase(BaseModel):
    file_name: str
    file_type: str

class ImportRecordCreate(ImportRecordBase):
    file_path: str
    file_hash: str

class ImportRecordResponse(ImportRecordBase):
    id: int
    file_path: str
    file_hash: str
    import_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# For preview data
class ParsedTransaction(BaseModel):
    """解析后的交易记录（预览用）"""
    row_number: int
    date: str
    amount: Decimal
    type: str  # "income" or "expense"
    merchant_name: str
    category: Optional[str] = None
    category_confidence: float = 0.0
    note: Optional[str] = None
    raw_data: dict

class ImportPreviewResponse(BaseModel):
    """导入预览响应"""
    import_record: ImportRecordResponse
    transactions: List[ParsedTransaction]
    total_income: Decimal
    total_expense: Decimal
    record_count: int
```

**Step 4: Create StorageBackend service**

```python
# app/services/storage.py
import os
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from pathlib import Path
from datetime import timedelta
import minio
from app.core.config import settings

class StorageBackend(ABC):
    """存储后端抽象类"""
    
    @abstractmethod
    def save(self, file: BinaryIO, filename: str, user_id: int) -> str:
        """保存文件，返回文件路径"""
        pass
    
    @abstractmethod
    def get(self, file_path: str) -> bytes:
        """获取文件内容"""
        pass
    
    @abstractmethod
    def delete(self, file_path: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    def generate_url(self, file_path: str, expires: int = 3600) -> str:
        """生成下载链接"""
        pass

class LocalStorageBackend(StorageBackend):
    """本地文件系统存储"""
    
    def __init__(self):
        self.base_path = Path(settings.STORAGE_LOCAL_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_id: int) -> Path:
        user_dir = self.base_path / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def save(self, file: BinaryIO, filename: str, user_id: int) -> str:
        user_dir = self._get_user_dir(user_id)
        file_path = user_dir / filename
        
        # Write file
        content = file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Return relative path from base_path
        return str(file_path.relative_to(self.base_path))
    
    def get(self, file_path: str) -> bytes:
        full_path = self.base_path / file_path
        with open(full_path, 'rb') as f:
            return f.read()
    
    def delete(self, file_path: str) -> bool:
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    def generate_url(self, file_path: str, expires: int = 3600) -> str:
        # Local files don't need URL generation, return file path
        return str(self.base_path / file_path)

class MinIOStorageBackend(StorageBackend):
    """MinIO对象存储"""
    
    def __init__(self):
        self.client = minio.Minio(
            settings.STORAGE_MINIO_ENDPOINT,
            access_key=settings.STORAGE_MINIO_ACCESS_KEY,
            secret_key=settings.STORAGE_MINIO_SECRET_KEY,
            secure=settings.STORAGE_MINIO_SECURE
        )
        self.bucket = settings.STORAGE_MINIO_BUCKET
        # Ensure bucket exists
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
    
    def save(self, file: BinaryIO, filename: str, user_id: int) -> str:
        content = file.read()
        object_name = f"{user_id}/{filename}"
        
        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(content),
            length=len(content)
        )
        return object_name
    
    def get(self, file_path: str) -> bytes:
        response = self.client.get_object(self.bucket, file_path)
        return response.read()
    
    def delete(self, file_path: str) -> bool:
        try:
            self.client.remove_object(self.bucket, file_path)
            return True
        except:
            return False
    
    def generate_url(self, file_path: str, expires: int = 3600) -> str:
        return self.client.presigned_get_object(self.bucket, file_path, expires=timedelta(seconds=expires))

# Factory function
def get_storage_backend() -> StorageBackend:
    if settings.STORAGE_TYPE == "minio":
        return MinIOStorageBackend()
    return LocalStorageBackend()

# File hashing utility
def calculate_file_hash(file: BinaryIO) -> str:
    """计算文件的SHA256哈希"""
    file.seek(0)
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: file.read(8192), b''):
        sha256.update(chunk)
    file.seek(0)
    return sha256.hexdigest()
```

**Step 5: Add models/__init__.py export**

Add to `app/models/__init__.py`:
```python
from app.models.import_record import ImportRecord, ImportStatus
```

**Step 6: Commit**

```bash
git add app/core/config.py app/models/import_record.py app/schemas/import_record.py app/services/storage.py app/models/__init__.py
git commit -m "feat(import): add ImportRecord model and StorageBackend"
```

---

## Task 2: Backend - BillParser Service

**Files:**
- Create: `app/services/bill_parser.py` - BillParser service

**Step 1: Create BillParser service**

```python
# app/services/bill_parser.py
import csv
import io
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import pandas as pd
from openpyxl import load_workbook

class BillParser(ABC):
    """账单解析器抽象类"""
    
    @abstractmethod
    def parse(self, content: bytes) -> List[Dict]:
        """解析文件内容，返回交易列表"""
        pass
    
    @abstractmethod
    def detect_type(self, content: bytes) -> str:
        """检测账单类型: alipay, wechat, unknown"""
        pass

class AlipayCSVParser(BillParser):
    """支付宝CSV解析器"""
    
    # 支付宝CSV列名映射
    COLUMN_MAPPING = {
        '交易号': 'transaction_id',
        '商户订单号': 'merchant_order_no',
        '创建时间': 'created_time',
        '完成时间': 'completed_time',
        '商品说明': 'description',
        '商品名称': 'product_name',
        '对方账户': 'counterparty',
        '金额': 'amount',
        '状态': 'status',
        '备注': 'note',
    }
    
    def detect_type(self, content: bytes) -> str:
        return "alipay"
    
    def parse(self, content: bytes) -> List[Dict]:
        decoded = content.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))
        
        transactions = []
        for row in reader:
            # Skip non-transaction rows
            if row.get('状态') != '交易成功':
                continue
            
            amount_str = row.get('金额', '0')
            if not amount_str:
                continue
            
            # Parse amount (handle negative for expense)
            amount = abs(Decimal(amount_str))
            
            # Determine type based on amount sign in original
            is_expense = '-' in amount_str or Decimal(amount_str) < 0
            
            # Parse date
            date_str = row.get('完成时间') or row.get('创建时间', '')
            try:
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        parsed_date = datetime.strptime(date_str.split('.')[0], fmt)
                        date = parsed_date.date()
                        break
                    except:
                        continue
                else:
                    date = datetime.now().date()
            except:
                date = datetime.now().date()
            
            transactions.append({
                'date': date.isoformat(),
                'amount': str(amount),
                'type': 'expense' if is_expense else 'income',
                'merchant_name': row.get('商品名称') or row.get('商品说明', ''),
                'counterparty': row.get('对方账户', ''),
                'note': row.get('备注', '') or row.get('商品说明', ''),
                'transaction_id': row.get('交易号', ''),
            })
        
        return transactions

class WeChatCSVParser(BillParser):
    """微信CSV解析器"""
    
    def detect_type(self, content: bytes) -> str:
        return "wechat"
    
    def parse(self, content: bytes) -> List[Dict]:
        decoded = content.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))
        
        transactions = []
        for row in reader:
            # Skip header or empty rows
            if row.get('交易状态') != '交易成功':
                continue
            
            amount_str = row.get('金额(元)', '0')
            if not amount_str:
                continue
            
            amount = abs(Decimal(amount_str))
            
            # Determine type
            is_expense = row.get('收/支') == '支出'
            
            # Parse date
            date_str = row.get('交易时间', '')
            try:
                parsed_date = datetime.strptime(date_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                date = parsed_date.date()
            except:
                date = datetime.now().date()
            
            transactions.append({
                'date': date.isoformat(),
                'amount': str(amount),
                'type': 'expense' if is_expense else 'income',
                'merchant_name': row.get('交易对方', ''),
                'counterparty': row.get('交易对方', ''),
                'note': row.get('备注', ''),
                'transaction_id': row.get('交易单号', ''),
            })
        
        return transactions

class ExcelParser(BillParser):
    """Excel解析器 - 自动检测格式"""
    
    def detect_type(self, content: bytes) -> str:
        # Load and check first row to detect format
        wb = load_workbook(io.BytesIO(content), read_only=True)
        ws = wb.active
        headers = [cell.value for cell in ws[1]] if ws.max_row > 0 else []
        
        if '支付宝' in str(headers) or '交易号' in str(headers):
            return "alipay"
        elif '微信' in str(headers) or '交易单号' in str(headers):
            return "wechat"
        
        return "unknown"
    
    def parse(self, content: bytes) -> List[Dict]:
        # Auto-detect and delegate
        wb = load_workbook(io.BytesIO(content), read_only=True)
        ws = wb.active
        
        # Convert to CSV-like format
        headers = [cell.value for cell in ws[1]] if ws.max_row > 0 else []
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if any(row):
                rows.append(dict(zip(headers, row)))
        
        # Use appropriate parser based on headers
        if '交易号' in headers or '支付宝' in str(headers):
            return self._parse_as_csv(rows, 'alipay')
        elif '交易单号' in headers or '微信' in str(headers):
            return self._parse_as_csv(rows, 'wechat')
        
        return []
    
    def _parse_as_csv(self, rows: List[Dict], bill_type: str) -> List[Dict]:
        if bill_type == 'alipay':
            parser = AlipayCSVParser()
            # Convert dict rows back to CSV format
            return parser.parse('\n'.join([','.join(r.keys())] + [','.join(str(v) for v in r.values()) for r in rows]).encode())
        elif bill_type == 'wechat':
            parser = WeChatCSVParser()
            return parser.parse('\n'.join([','.join(r.keys())] + [','.join(str(v) for v in r.values()) for r in rows]).encode())
        return []

def get_parser(file_type: str) -> BillParser:
    """根据文件类型获取解析器"""
    parsers = {
        'csv': AlipayCSVParser(),  # Default CSV parser
        'xlsx': ExcelParser(),
        'xls': ExcelParser(),
    }
    return parsers.get(file_type, AlipayCSVParser())

def parse_bill(content: bytes, file_type: str) -> Tuple[str, List[Dict]]:
    """解析账单文件，自动检测类型"""
    parser = get_parser(file_type)
    
    # Try to detect actual type
    detected_type = parser.detect_type(content) if hasattr(parser, 'detect_type') else file_type
    
    # Use appropriate parser for detected type
    if detected_type == 'wechat':
        parser = WeChatCSVParser()
    elif detected_type == 'alipay':
        parser = AlipayCSVParser()
    
    transactions = parser.parse(content)
    return detected_type, transactions
```

**Step 2: Commit**

```bash
git add app/services/bill_parser.py
git commit -m "feat(import): add BillParser service for CSV/Excel parsing"
```

---

## Task 3: Backend - Keyword Classification & AI Fallback

**Files:**
- Create: `app/services/categorizer.py` - Keyword + AI classification

**Step 1: Create categorizer service**

```python
# app/services/categorizer.py
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.category import Category
import re

# Keyword to category mapping (expandable)
KEYWORD_CATEGORY_MAP = {
    # 餐饮
    '餐饮': ['餐饮', '美食', '快餐', '小吃', '火锅', '烧烤', '外卖', '星巴克', '麦当劳', '肯德基', '瑞幸', '奈雪', '喜茶'],
    '餐饮': [' restaurant', 'cafe', 'coffee', 'mcdonald', 'kfc', 'starbucks'],
    
    # 交通
    '交通': ['交通', '打车', '滴滴', '出租车', '地铁', '公交', '高铁', '火车', '机票', '加油', '停车'],
    '交通': [' taxi', 'uber', 'didi', 'subway', 'metro', 'gas', 'parking'],
    
    # 购物
    '购物': ['购物', '淘宝', '天猫', '京东', '拼多多', '唯品会', '苏宁', '商城', '超市', '便利店', '百货'],
    '购物': ['taobao', 'jd.com', 'tmall', 'shopping', 'mall', 'store'],
    
    # 娱乐
    '娱乐': ['娱乐', '电影', 'KTV', '酒吧', '网吧', '游戏', '旅游', '酒店', '民宿', '门票'],
    '娱乐': ['movie', 'cinema', 'ktv', 'bar', 'game', 'hotel', 'travel'],
    
    # 医疗
    '医疗': ['医疗', '医院', '药店', '诊所', '体检', '保险'],
    '医疗': ['hospital', 'pharmacy', 'medical', 'clinic'],
    
    # 教育
    '教育': ['教育', '培训', '学费', '书', '课程', '教育'],
    '教育': ['education', 'course', 'book', 'school', 'tuition'],
    
    # 住房
    '住房': ['住房', '房租', '水电', '物业', '燃气', '宽带', '话费'],
    '住房': ['rent', 'utilities', 'electricity', 'water', 'property'],
    
    # 工资
    '工资': ['工资', '薪资', '退休金', '养老金'],
    '工资': ['salary', 'payroll', 'pension'],
    
    # 投资
    '投资': ['投资', '理财', '基金', '股票', '债券', '利息', '分红'],
    '投资': ['investment', 'fund', 'stock', 'dividend', 'interest'],
    
    # 通讯
    '通讯': ['通讯', '话费', '流量', '宽带', '电信', '移动', '联通'],
    '通讯': ['mobile', 'phone', 'telecom'],
}

# Flatten keyword map for faster lookup
FLAT_KEYWORD_MAP = {}
for category, keywords_list in KEYWORD_CATEGORY_MAP.items():
    for keyword in keywords_list:
        FLAT_KEYWORD_MAP[keyword.lower()] = category

def classify_by_keyword(merchant_name: str, note: str = '') -> Tuple[Optional[str], float]:
    """
    基于关键词分类
    返回: (category_name, confidence)
    """
    if not merchant_name and not note:
        return None, 0.0
    
    search_text = f"{merchant_name} {note}".lower()
    
    # Exact match first
    for keyword, category in FLAT_KEYWORD_MAP.items():
        if keyword in search_text:
            return category, 0.9
    
    # Fuzzy match (partial)
    for keyword, category in FLAT_KEYWORD_MAP.items():
        if len(keyword) >= 2 and keyword in search_text:
            return category, 0.7
    
    return None, 0.0

def classify_with_ai(merchant_name: str, note: str = '', transaction_type: str = 'expense') -> Tuple[Optional[str], float]:
    """
    AI分类占位符 - 当关键词匹配失败时使用
    可以后续接入OpenAI/Claude等AI服务
    
    返回: (category_name, confidence)
    """
    # TODO: Integrate with AI service
    # For now, return default categories based on type
    if transaction_type == 'income':
        return '其他收入', 0.3
    return '其他', 0.3

def auto_classify(
    merchant_name: str, 
    note: str = '', 
    transaction_type: str = 'expense',
    db: Session = None
) -> Tuple[Optional[str], float]:
    """
    自动分类 - 关键词优先，AI兜底
    
    返回: (category_name, confidence)
    """
    # Step 1: Keyword-based classification
    category, confidence = classify_by_keyword(merchant_name, note)
    if category:
        return category, confidence
    
    # Step 2: AI fallback
    return classify_with_ai(merchant_name, note, transaction_type)
```

**Step 2: Commit**

```bash
git add app/services/categorizer.py
git commit -m "feat(import): add keyword-based auto-classification service"
```

---

## Task 4: Backend - Import API

**Files:**
- Create: `app/api/imports.py` - Import API endpoints

**Step 1: Create imports API**

```python
# app/api/imports.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.import_record import ImportRecord, ImportStatus
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.import_record import (
    ImportRecordCreate, 
    ImportRecordResponse,
    ParsedTransaction,
    ImportPreviewResponse
)
from app.services.storage import get_storage_backend, calculate_file_hash
from app.services.bill_parser import parse_bill
from app.services.categorizer import auto_classify

router = APIRouter()

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
MIME_TYPES = {
    'text/csv': 'csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xls',
}

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传文件，返回导入记录ID
    """
    # Validate file extension
    import os
    filename = file.filename.lower()
    _, ext = os.path.splitext(filename)
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {ext}。支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Determine file type
    file_type = ext[1:]  # Remove leading dot
    
    # Read and hash file
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check for duplicate
    existing = db.query(ImportRecord).filter(
        ImportRecord.file_hash == file_hash,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="文件已存在，请勿重复上传"
        )
    
    # Save file
    storage = get_storage_backend()
    import hashlib
    file_obj = io.BytesIO(content)
    file_path = storage.save(file_obj, f"{file_hash}{ext}", current_user.id)
    
    # Create import record
    import_record = ImportRecord(
        file_name=file.filename,
        file_type=file_type,
        file_path=file_path,
        file_hash=file_hash,
        user_id=current_user.id,
        status=ImportStatus.PENDING
    )
    
    db.add(import_record)
    db.commit()
    db.refresh(import_record)
    
    return {"id": import_record.id, "file_name": import_record.file_name}

@router.get("/{import_id}/preview", response_model=ImportPreviewResponse)
def preview_import(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    预览解析后的交易数据
    """
    # Get import record
    import_record = db.query(ImportRecord).filter(
        ImportRecord.id == import_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入记录不存在"
        )
    
    # Get file content
    storage = get_storage_backend()
    content = storage.get(import_record.file_path)
    
    # Parse bill
    bill_type, transactions = parse_bill(content, import_record.file_type)
    
    # Auto-classify each transaction
    parsed_transactions = []
    total_income = Decimal('0')
    total_expense = Decimal('0')
    
    for idx, trans in enumerate(transactions, 1):
        # Get category
        category_name, confidence = auto_classify(
            trans.get('merchant_name', ''),
            trans.get('note', ''),
            trans.get('type', 'expense'),
            db
        )
        
        amount = Decimal(trans.get('amount', '0'))
        if trans.get('type') == 'income':
            total_income += amount
        else:
            total_expense += amount
        
        parsed_transactions.append(ParsedTransaction(
            row_number=idx,
            date=trans.get('date', ''),
            amount=amount,
            type=trans.get('type', 'expense'),
            merchant_name=trans.get('merchant_name', ''),
            category=category_name,
            category_confidence=confidence,
            note=trans.get('note', ''),
            raw_data=trans
        ))
    
    # Update status
    import_record.status = ImportStatus.PARSED
    db.commit()
    
    return ImportPreviewResponse(
        import_record=import_record,
        transactions=parsed_transactions,
        total_income=total_income,
        total_expense=total_expense,
        record_count=len(parsed_transactions)
    )

@router.post("/{import_id}/confirm", response_model=List[dict])
def confirm_import(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    确认导入，创建交易记录
    """
    # Get import record
    import_record = db.query(ImportRecord).filter(
        ImportRecord.id == import_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入记录不存在"
        )
    
    if import_record.status != ImportStatus.PARSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该导入记录尚未预览，请先预览"
        )
    
    # Get file content
    storage = get_storage_backend()
    content = storage.get(import_record.file_path)
    
    # Parse bill
    _, transactions = parse_bill(content, import_record.file_type)
    
    # Create transactions
    created_ids = []
    for trans in transactions:
        # Find or create category
        category_name, _ = auto_classify(
            trans.get('merchant_name', ''),
            trans.get('note', ''),
            trans.get('type', 'expense'),
            db
        )
        
        category = db.query(Category).filter(
            Category.name == category_name,
            Category.type == trans.get('type', 'expense')
        ).first()
        
        if not category:
            # Use default category
            category = db.query(Category).filter(
                Category.name == '其他' if trans.get('type') == 'expense' else '其他收入',
                Category.type == trans.get('type', 'expense')
            ).first()
        
        # Parse date
        from datetime import datetime
        try:
            trans_date = datetime.fromisoformat(trans.get('date')).date()
        except:
            trans_date = datetime.now().date()
        
        # Create transaction
        transaction = Transaction(
            amount=Decimal(trans.get('amount', '0')),
            type=trans.get('type', 'expense'),
            category_id=category.id if category else 1,
            date=trans_date,
            note=trans.get('note', '') or trans.get('merchant_name', '')
        )
        
        db.add(transaction)
        db.flush()
        created_ids.append(transaction.id)
    
    # Update import record
    import_record.status = ImportStatus.CONFIRMED
    import_record.import_count = len(created_ids)
    db.commit()
    
    return [{"id": id} for id in created_ids]

@router.get("/history", response_model=List[ImportRecordResponse])
def get_import_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取导入历史
    """
    records = db.query(ImportRecord).filter(
        ImportRecord.user_id == current_user.id
    ).order_by(ImportRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return records
```

**Step 2: Fix missing imports**

Add to top of imports.py:
```python
import hashlib
import io
```

**Step 3: Register router in main.py**

Modify `app/main.py`:
```python
from app.api import users, categories, transactions, budgets, tags, time_periods, recycle_bin, imports
app.include_router(imports.router, prefix="/api/imports", tags=["imports"])
```

**Step 4: Commit**

```bash
git add app/api/imports.py app/main.py
git commit -m "feat(import): add Import API endpoints"
```

---

## Task 5: Backend - Files API

**Files:**
- Create: `app/api/files.py` - Files API endpoints

**Step 1: Create files API**

```python
# app/api/files.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.import_record import ImportRecord
from app.schemas.import_record import ImportRecordResponse
from app.services.storage import get_storage_backend

router = APIRouter()

@router.get("/", response_model=List[ImportRecordResponse])
def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    列出用户已导入的文件
    """
    records = db.query(ImportRecord).filter(
        ImportRecord.user_id == current_user.id
    ).order_by(ImportRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return records

@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载已导入的文件
    """
    record = db.query(ImportRecord).filter(
        ImportRecord.id == file_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    storage = get_storage_backend()
    content = storage.get(record.file_path)
    
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={record.file_name}"}
    )

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除导入的文件和记录
    """
    record = db.query(ImportRecord).filter(
        ImportRecord.id == file_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # Delete physical file
    storage = get_storage_backend()
    storage.delete(record.file_path)
    
    # Delete record
    db.delete(record)
    db.commit()
    
    return None
```

**Step 2: Register router in main.py**

```python
from app.api import users, categories, transactions, budgets, tags, time_periods, recycle_bin, imports, files
app.include_router(files.router, prefix="/api/files", tags=["files"])
```

**Step 3: Commit**

```bash
git add app/api/files.py app/main.py
git commit -m "feat(import): add Files API endpoints"
```

---

## Task 6: Frontend - API Service

**Files:**
- Create: `webui/src/services/import.service.ts` - Import API service

**Step 1: Create import service**

```typescript
// webui/src/services/import.service.ts
import axios from './api'
import type { AxiosProgressEvent } from 'axios'

export interface ParsedTransaction {
  row_number: number
  date: string
  amount: string
  type: 'income' | 'expense'
  merchant_name: string
  category: string | null
  category_confidence: number
  note: string | null
  raw_data: Record<string, any>
}

export interface ImportRecord {
  id: number
  file_name: string
  file_type: string
  file_path: string
  file_hash: string
  import_count: number
  status: 'pending' | 'parsed' | 'confirmed' | 'failed'
  error_message?: string
  created_at: string
  updated_at?: string
}

export interface ImportPreview {
  import_record: ImportRecord
  transactions: ParsedTransaction[]
  total_income: string
  total_expense: string
  record_count: number
}

export const importService = {
  // Upload file
  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<{ id: number; file_name: string }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post('/imports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  },

  // Preview import
  async getPreview(importId: number): Promise<ImportPreview> {
    const response = await axios.get(`/imports/${importId}/preview`)
    return response.data
  },

  // Confirm import
  async confirmImport(importId: number): Promise<{ id: number }[]> {
    const response = await axios.post(`/imports/${importId}/confirm`)
    return response.data
  },

  // Get import history
  async getHistory(skip = 0, limit = 20): Promise<ImportRecord[]> {
    const response = await axios.get('/imports/history', {
      params: { skip, limit },
    })
    return response.data
  },

  // List files
  async listFiles(skip = 0, limit = 20): Promise<ImportRecord[]> {
    const response = await axios.get('/files/', {
      params: { skip, limit },
    })
    return response.data
  },

  // Download file
  async downloadFile(fileId: number): Promise<Blob> {
    const response = await axios.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  // Delete file
  async deleteFile(fileId: number): Promise<void> {
    await axios.delete(`/files/${fileId}`)
  },
}
```

**Step 2: Commit**

```bash
git add webui/src/services/import.service.ts
git commit -m "feat(frontend): add import service API client"
```

---

## Task 7: Frontend - Import View Components

**Files:**
- Create: `webui/src/views/ImportView.vue` - Main import view
- Create: `webui/src/components/import/ImportDropzone.vue` - Drag & drop upload
- Create: `webui/src/components/import/ImportPreview.vue` - Preview table
- Create: `webui/src/components/import/ImportHistory.vue` - History list
- Create: `webui/src/stores/import.ts` - Import state store
- Modify: `webui/src/router/index.ts` - Add import route
- Modify: `webui/src/App.vue` - Add navigation item

**Step 1: Create import store**

```typescript
// webui/src/stores/import.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ImportRecord, ImportPreview, ParsedTransaction } from '@/services/import.service'

export const useImportStore = defineStore('import', () => {
  // State
  const currentImport = ref<ImportPreview | null>(null)
  const history = ref<ImportRecord[]>([])
  const isLoading = ref(false)
  const uploadProgress = ref(0)
  
  // Getters
  const hasCurrentImport = computed(() => currentImport.value !== null)
  const transactionCount = computed(() => currentImport.value?.record_count ?? 0)
  
  // Actions
  function setCurrentImport(preview: ImportPreview | null) {
    currentImport.value = preview
  }
  
  function clearCurrentImport() {
    currentImport.value = null
  }
  
  function setHistory(records: ImportRecord[]) {
    history.value = records
  }
  
  function addToHistory(record: ImportRecord) {
    history.value.unshift(record)
  }
  
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }
  
  function setUploadProgress(progress: number) {
    uploadProgress.value = progress
  }
  
  return {
    currentImport,
    history,
    isLoading,
    uploadProgress,
    hasCurrentImport,
    transactionCount,
    setCurrentImport,
    clearCurrentImport,
    setHistory,
    addToHistory,
    setLoading,
    setUploadProgress,
  }
})
```

**Step 2: Create ImportDropzone component**

```vue
<!-- webui/src/components/import/ImportDropzone.vue -->
<template>
  <div
    class="import-dropzone"
    :class="{ 'is-dragging': isDragging, 'is-uploading': isUploading }"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="openFilePicker"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="acceptedTypes"
      @change="onFileSelect"
      hidden
    />
    
    <div v-if="isUploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
      <span class="progress-text">正在上传... {{ progress }}%</span>
    </div>
    
    <div v-else class="dropzone-content">
      <div class="icon">📁</div>
      <div class="text">
        <p class="primary">拖拽文件到此处上传</p>
        <p class="secondary">或点击选择文件</p>
      </div>
      <div class="supported-types">
        支持格式: CSV, XLSX, XLS (支付宝/微信账单)
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { importService } from '@/services/import.service'
import { useImportStore } from '@/stores/import'

const emit = defineEmits<{
  (e: 'uploaded', id: number, fileName: string): void
  (e: 'error', message: string): void
}>()

const importStore = useImportStore()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)
const progress = ref(0)
const acceptedTypes = '.csv,.xlsx,.xls'

const openFilePicker = () => {
  if (!isUploading.value) {
    fileInput.value?.click()
  }
}

const onDragEnter = () => {
  isDragging.value = true
}

const onDragOver = () => {
  isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = async (event: DragEvent) => {
  isDragging.value = false
  
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    await uploadFile(files[0])
  }
}

const onFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    await uploadFile(files[0])
  }
  // Reset input
  target.value = ''
}

const uploadFile = async (file: File) => {
  isUploading.value = true
  progress.value = 0
  importStore.setUploadProgress(0)
  
  try {
    const result = await importService.uploadFile(file, (p) => {
      progress.value = p
      importStore.setUploadProgress(p)
    })
    
    emit('uploaded', result.id, result.file_name)
  } catch (error: any) {
    const message = error.response?.data?.detail || '上传失败，请重试'
    emit('error', message)
  } finally {
    isUploading.value = false
    progress.value = 0
    importStore.setUploadProgress(0)
  }
}
</script>

<style scoped>
.import-dropzone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fafafa;
}

.import-dropzone:hover,
.import-dropzone.is-dragging {
  border-color: #3b82f6;
  background: #eff6ff;
}

.import-dropzone.is-uploading {
  cursor: default;
  border-style: solid;
}

.dropzone-content .icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.dropzone-content .text .primary {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin: 0 0 4px;
}

.dropzone-content .text .secondary {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.supported-types {
  margin-top: 16px;
  font-size: 12px;
  color: #9ca3af;
}

.upload-progress {
  padding: 0 24px;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  color: #6b7280;
}
</style>
```

**Step 3: Create ImportPreview component**

```vue
<!-- webui/src/components/import/ImportPreview.vue -->
<template>
  <div class="import-preview">
    <div class="preview-header">
      <div class="summary">
        <div class="stat">
          <span class="label">总收入</span>
          <span class="value income">+¥{{ formatAmount(preview.total_income) }}</span>
        </div>
        <div class="stat">
          <span class="label">总支出</span>
          <span class="value expense">-¥{{ formatAmount(preview.total_expense) }}</span>
        </div>
        <div class="stat">
          <span class="label">记录数</span>
          <span class="value">{{ preview.record_count }}</span>
        </div>
      </div>
      
      <div class="actions">
        <button class="btn btn-secondary" @click="onCancel">取消</button>
        <button class="btn btn-primary" @click="onConfirm" :disabled="isConfirming">
          {{ isConfirming ? '导入中...' : '确认导入' }}
        </button>
      </div>
    </div>
    
    <div class="preview-table-container">
      <table class="preview-table">
        <thead>
          <tr>
            <th>#</th>
            <th>日期</th>
            <th>类型</th>
            <th>金额</th>
            <th>商家/备注</th>
            <th>分类</th>
            <th>可信度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trans in preview.transactions" :key="trans.row_number">
            <td>{{ trans.row_number }}</td>
            <td>{{ trans.date }}</td>
            <td>
              <span :class="['type-badge', trans.type]">
                {{ trans.type === 'income' ? '收入' : '支出' }}
              </span>
            </td>
            <td :class="trans.type">¥{{ formatAmount(trans.amount.toString()) }}</td>
            <td class="merchant">{{ trans.merchant_name || trans.note || '-' }}</td>
            <td>
              <span class="category">{{ trans.category || '未分类' }}</span>
            </td>
            <td>
              <span :class="['confidence', getConfidenceClass(trans.category_confidence)]">
                {{ Math.round(trans.category_confidence * 100) }}%
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ImportPreview } from '@/services/import.service'
import { importService } from '@/services/import.service'
import { useImportStore } from '@/stores/import'

const props = defineProps<{
  preview: ImportPreview
}>()

const emit = defineEmits<{
  (e: 'confirmed', count: number): void
  (e: 'cancel'): void
  (e: 'error', message: string): void
}>()

const importStore = useImportStore()
const isConfirming = ref(false)

const formatAmount = (amount: string) => {
  return parseFloat(amount).toFixed(2)
}

const getConfidenceClass = (confidence: number) => {
  if (confidence >= 0.8) return 'high'
  if (confidence >= 0.5) return 'medium'
  return 'low'
}

const onCancel = () => {
  emit('cancel')
}

const onConfirm = async () => {
  isConfirming.value = true
  
  try {
    const result = await importService.confirmImport(props.preview.import_record.id)
    importStore.clearCurrentImport()
    emit('confirmed', result.length)
  } catch (error: any) {
    const message = error.response?.data?.detail || '导入失败，请重试'
    emit('error', message)
  } finally {
    isConfirming.value = false
  }
}
</script>

<style scoped>
.import-preview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.summary {
  display: flex;
  gap: 32px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat .label {
  font-size: 12px;
  color: #6b7280;
}

.stat .value {
  font-size: 18px;
  font-weight: 600;
}

.stat .value.income {
  color: #10b981;
}

.stat .value.expense {
  color: #ef4444;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.preview-table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.preview-table th,
.preview-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.preview-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.preview-table tr:last-child td {
  border-bottom: none;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.type-badge.income {
  background: #d1fae5;
  color: #059669;
}

.type-badge.expense {
  background: #fee2e2;
  color: #dc2626;
}

.income {
  color: #10b981;
}

.expense {
  color: #ef4444;
}

.merchant {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category {
  color: #6b7280;
}

.confidence {
  font-size: 12px;
}

.confidence.high {
  color: #10b981;
}

.confidence.medium {
  color: #f59e0b;
}

.confidence.low {
  color: #6b7280;
}
</style>
```

**Step 4: Create ImportHistory component**

```vue
<!-- webui/src/components/import/ImportHistory.vue -->
<template>
  <div class="import-history">
    <div class="history-header">
      <h3>导入历史</h3>
    </div>
    
    <div v-if="isLoading" class="loading">加载中...</div>
    
    <div v-else-if="records.length === 0" class="empty">
      <p>暂无导入记录</p>
    </div>
    
    <div v-else class="history-list">
      <div v-for="record in records" :key="record.id" class="history-item">
        <div class="file-info">
          <div class="file-icon">{{ getFileIcon(record.file_type) }}</div>
          <div class="file-details">
            <div class="file-name">{{ record.file_name }}</div>
            <div class="file-meta">
              {{ formatDate(record.created_at) }} · {{ record.import_count }} 条记录
            </div>
          </div>
        </div>
        
        <div class="status">
          <span :class="['status-badge', record.status]">
            {{ getStatusText(record.status) }}
          </span>
        </div>
        
        <div class="actions">
          <button 
            v-if="record.status === 'parsed'" 
            class="btn btn-small"
            @click="$emit('retry', record.id)"
          >
            重试
          </button>
          <button 
            class="btn btn-small btn-danger"
            @click="$emit('delete', record.id)"
          >
            删除
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="hasMore" class="load-more">
      <button class="btn btn-secondary" @click="loadMore">加载更多</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ImportRecord } from '@/services/import.service'
import { importService } from '@/services/import.service'

defineProps<{
  records: ImportRecord[]
  isLoading?: boolean
  hasMore?: boolean
}>()

defineEmits<{
  (e: 'retry', id: number): void
  (e: 'delete', id: number): void
  (e: 'load-more'): void
}>()

const getFileIcon = (type: string) => {
  const icons: Record<string, string> = {
    csv: '📄',
    xlsx: '📊',
    xls: '📊',
  }
  return icons[type] || '📄'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    parsed: '已解析',
    confirmed: '已导入',
    failed: '失败',
  }
  return texts[status] || status
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const loadMore = () => {
  // Emit event to parent to handle
}
</script>

<style scoped>
.import-history {
  margin-top: 24px;
}

.history-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
  color: #1f2937;
}

.loading,
.empty {
  text-align: center;
  padding: 32px;
  color: #6b7280;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  gap: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-icon {
  font-size: 24px;
}

.file-name {
  font-weight: 500;
  color: #1f2937;
}

.file-meta {
  font-size: 12px;
  color: #6b7280;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.parsed {
  background: #dbeafe;
  color: #2563eb;
}

.status-badge.confirmed {
  background: #d1fae5;
  color: #059669;
}

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-small {
  padding: 4px 8px;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-danger {
  background: #fee2e2;
  color: #dc2626;
}

.btn-danger:hover {
  background: #fecaca;
}

.load-more {
  margin-top: 16px;
  text-align: center;
}
</style>
```

**Step 5: Create ImportView**

```vue
<!-- webui/src/views/ImportView.vue -->
<template>
  <div class="import-view">
    <div class="page-header">
      <h1>导入账单</h1>
      <p class="description">从支付宝或微信导出的CSV/Excel文件中批量导入交易记录</p>
    </div>
    
    <div v-if="!importStore.currentImport" class="upload-section">
      <ImportDropzone 
        @uploaded="onFileUploaded"
        @error="showError"
      />
      
      <ImportHistory 
        :records="importStore.history"
        :is-loading="isLoadingHistory"
        :has-more="hasMoreHistory"
        @retry="onRetry"
        @delete="onDelete"
      />
    </div>
    
    <div v-else class="preview-section">
      <ImportPreview 
        :preview="importStore.currentImport"
        @confirmed="onImportConfirmed"
        @cancel="onCancelImport"
        @error="showError"
      />
    </div>
    
    <!-- Toast notifications -->
    <div v-if="toast.show" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useImportStore } from '@/stores/import'
import { importService } from '@/services/import.service'
import ImportDropzone from '@/components/import/ImportDropzone.vue'
import ImportPreview from '@/components/import/ImportPreview.vue'
import ImportHistory from '@/components/import/ImportHistory.vue'

const importStore = useImportStore()

const isLoadingHistory = ref(false)
const hasMoreHistory = ref(false)
const toast = ref<{ show: boolean; message: string; type: string }>({
  show: false,
  message: '',
  type: 'success',
})

const showToast = (message: string, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const showError = (message: string) => {
  showToast(message, 'error')
}

const onFileUploaded = async (id: number, fileName: string) => {
  try {
    const preview = await importService.getPreview(id)
    importStore.setCurrentImport(preview)
    showToast(`文件 "${fileName}" 解析成功`)
  } catch (error: any) {
    showError(error.response?.data?.detail || '解析失败')
  }
}

const onImportConfirmed = (count: number) => {
  showToast(`成功导入 ${count} 条交易记录`)
  loadHistory()
}

const onCancelImport = () => {
  importStore.clearCurrentImport()
}

const onRetry = async (id: number) => {
  try {
    const preview = await importService.getPreview(id)
    importStore.setCurrentImport(preview)
  } catch (error: any) {
    showError(error.response?.data?.detail || '加载失败')
  }
}

const onDelete = async (id: number) => {
  if (!confirm('确定要删除这条导入记录吗？')) return
  
  try {
    await importService.deleteFile(id)
    showToast('删除成功')
    loadHistory()
  } catch (error: any) {
    showError(error.response?.data?.detail || '删除失败')
  }
}

const loadHistory = async () => {
  isLoadingHistory.value = true
  try {
    const records = await importService.getHistory()
    importStore.setHistory(records)
    hasMoreHistory.value = records.length >= 20
  } catch (error: any) {
    console.error('Failed to load history:', error)
  } finally {
    isLoadingHistory.value = false
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.import-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
  color: #1f2937;
}

.description {
  color: #6b7280;
  margin: 0;
}

.upload-section,
.preview-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
  z-index: 1000;
}

.toast.success {
  background: #10b981;
  color: white;
}

.toast.error {
  background: #ef4444;
  color: white;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
```

**Step 6: Add route**

Modify `webui/src/router/index.ts`:

```typescript
import ImportView from '@/views/ImportView.vue'

// Add route
{
  path: '/import',
  name: 'import',
  component: ImportView,
  meta: { requiresAuth: true }
}
```

**Step 7: Commit**

```bash
git add webui/src/views/ImportView.vue webui/src/components/import/ webui/src/stores/import.ts webui/src/services/import.service.ts webui/src/router/index.ts
git commit -m "feat(frontend): add import view and components"
```

---

## Task 8: Test & Verify

**Files:**
- Run tests and verify

**Step 1: Install dependencies**

```bash
cd /path/to/money
uv sync pandas openpyxl python-multipart minio
```

**Step 2: Run backend**

```bash
python -m uvicorn app.main:app --reload
```

**Step 3: Test API**

```bash
# Upload
curl -X POST -F "file=@alipay_bill.csv" http://localhost:8000/api/imports/upload

# Preview
curl http://localhost:8000/api/imports/{id}/preview

# Confirm
curl -X POST http://localhost:8000/api/imports/{id}/confirm
```

**Step 4: Build frontend**

```bash
cd webui
npm run build
```

**Step 5: Commit**

```bash
git add .
git commit -m "feat: complete CSV/Excel import feature"
```

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Backend config & storage (ImportRecord model, StorageBackend) |
| 2 | BillParser service (Alipay/WeChat CSV, Excel) |
| 3 | Keyword classification & AI fallback |
| 4 | Import API (upload, preview, confirm, history) |
| 5 | Files API (list, download, delete) |
| 6 | Frontend API service |
| 7 | Frontend components (ImportView, ImportDropzone, ImportPreview, ImportHistory) |
| 8 | Test & verify |

# Phase 5: Import/OCR/File Retention Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement import functionality for Alipay CSV, WeChat CSV, and Excel files with file retention, preview, and auto-categorization.

**Architecture:** 
- Backend: FastAPI with SQLAlchemy, storage service abstraction (local + MinIO), bill parser with format detection
- Frontend: Vue 3 with Pinia stores, drag & drop upload, preview/confirmation flow

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, Pinia, openpyxl, python-multipart, hashlib

---

## Task 1: Add Python Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add dependencies**

```toml
dependencies = [
    "bcrypt==4.0.1",
    "fastapi[standard]>=0.115.12",
    "passlib[bcrypt]>=1.7.4",
    "pydantic-settings>=2.13.1",
    "python-jose>=3.5.0",
    "sqlalchemy>=2.0.48",
    "python-multipart>=0.0.9",
    "openpyxl>=3.1.2",
    "pandas>=2.0.0",
    "minio>=7.1.0",
]
```

**Step 2: Install dependencies**

Run: `uv sync`

---

## Task 2: ImportRecord Model

**Files:**
- Create: `app/models/import_record.py`
- Modify: `app/models/__init__.py`
- Modify: `app/db/database.py` (if needed for Base import)

**Step 1: Create ImportRecord model**

```python
# app/models/import_record.py
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
```

**Step 2: Update Transaction model to link to ImportRecord**

Modify: `app/models/transaction.py`

Add to Transaction class:
```python
import_record_id = Column(Integer, ForeignKey('import_records.id'))
import_record = relationship("ImportRecord", back_populates="transactions")
```

**Step 3: Update models __init__**

Modify: `app/models/__init__.py`

```python
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.tag import Tag
from app.models.time_period import TimePeriod
from app.models.import_record import ImportRecord

__all__ = ["User", "Category", "Transaction", "Budget", "Tag", "TimePeriod", "ImportRecord"]
```

---

## Task 3: Storage Service

**Files:**
- Create: `app/services/storage.py`

**Step 1: Create storage service**

```python
# app/services/storage.py
import os
import hashlib
from typing import Optional
from datetime import timedelta
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

class StorageService:
    """存储服务 - 支持本地和MinIO"""
    
    def __init__(self):
        self.use_minio = getattr(settings, 'MINIO_ENABLED', False)
        self.base_path = Path("data/imports")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        if self.use_minio:
            self.minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            self.bucket_name = settings.MINIO_BUCKET
    
    def _compute_hash(self, content: bytes) -> str:
        """计算文件SHA256哈希"""
        return hashlib.sha256(content).hexdigest()
    
    def save_file(self, user_id: int, file_content: bytes, filename: str) -> tuple[str, str]:
        """
        保存文件，返回(file_path, file_hash)
        """
        file_hash = self._compute_hash(file_content)
        
        if self.use_minio:
            return self._save_to_minio(user_id, file_content, filename, file_hash)
        else:
            return self._save_to_local(user_id, file_content, filename, file_hash)
    
    def _save_to_local(self, user_id: int, content: bytes, filename: str, file_hash: str) -> tuple[str, str]:
        user_dir = self.base_path / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用hash作为文件名避免重复
        ext = Path(filename).suffix
        safe_filename = f"{file_hash[:16]}{ext}"
        file_path = user_dir / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return str(file_path), file_hash
    
    def _save_to_minio(self, user_id: int, content: bytes, filename: str, file_hash: str) -> tuple[str, str]:
        import io
        ext = Path(filename).suffix
        object_name = f"{user_id}/{file_hash[:16]}{ext}"
        
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error:
            self.minio_client.make_bucket(self.bucket_name)
        
        self.minio_client.put_object(
            self.bucket_name,
            object_name,
            io.BytesIO(content),
            len(content)
        )
        
        return f"minio://{self.bucket_name}/{object_name}", file_hash
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """获取文件内容"""
        if self.use_minio and file_path.startswith("minio://"):
            return self._get_from_minio(file_path)
        else:
            return self._get_from_local(file_path)
    
    def _get_from_local(self, file_path: str) -> Optional[bytes]:
        path = Path(file_path)
        if path.exists():
            return path.read_bytes()
        return None
    
    def _get_from_minio(self, minio_path: str) -> Optional[bytes]:
        parts = minio_path.replace("minio://", "").split("/", 1)
        if len(parts) != 2:
            return None
        bucket, object_name = parts
        try:
            response = self.minio_client.get_object(bucket, object_name)
            return response.read()
        except S3Error:
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        if self.use_minio and file_path.startswith("minio://"):
            return self._delete_from_minio(file_path)
        else:
            return self._delete_from_local(file_path)
    
    def _delete_from_local(self, file_path: str) -> bool:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def _delete_from_minio(self, minio_path: str) -> bool:
        parts = minio_path.replace("minio://", "").split("/", 1)
        if len(parts) != 2:
            return False
        bucket, object_name = parts
        try:
            self.minio_client.remove_object(bucket, object_name)
            return True
        except S3Error:
            return False

storage_service = StorageService()
```

**Step 2: Update config for MinIO**

Modify: `app/core/config.py`

Add:
```python
# MinIO 配置
MINIO_ENABLED: bool = False
MINIO_ENDPOINT: str = "localhost:9000"
MINIO_ACCESS_KEY: str = ""
MINIO_SECRET_KEY: str = ""
MINIO_SECURE: bool = False
MINIO_BUCKET: str = "money-imports"

# 上传配置
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS: list[str] = [".csv", ".xlsx", ".xls"]
```

---

## Task 4: Bill Parser Service

**Files:**
- Create: `app/services/bill_parser.py`

**Step 1: Create bill parser**

```python
# app/services/bill_parser.py
import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

from app.models.category import Category

# 类别关键词映射
CATEGORY_KEYWORDS = {
    "餐饮": ["午餐", "晚餐", "早餐", "外卖", "餐厅", "麦当劳", "肯德基", "星巴克", "瑞幸", "奶茶", "小吃", "烧烤", "火锅", "冒菜", "黄焖鸡", "沙县", "兰州拉面", "便利店", "全家", "罗森", "7-11"],
    "交通": ["地铁", "公交", "出租车", "滴滴", "加油", "停车", "高速", "打车", "网约车", "共享单车", "火车", "高铁", "飞机", "长途"],
    "购物": ["淘宝", "京东", "拼多多", "天猫", "超市", "苏宁", "国美", "唯品会", "蘑菇街", "网易严选", "小米", "苹果", "华为"],
    "娱乐": ["电影", "游戏", "KTV", "音乐", "视频", "爱奇艺", "优酷", "腾讯视频", "B站", "网易云", "QQ音乐", "健身", "游泳", "羽毛球", "篮球", "足球"],
    "住房": ["房租", "水电", "燃气", "物业", "宽带", "话费", "中介", "维修", "保洁"],
    "医疗": ["药店", "医院", "门诊", "体检", "保险", "医保", "牙科", "眼科"],
    "教育": ["学费", "培训", "课程", "书籍", "文具", "教育", "辅导", "留学"],
    "工资": ["工资", "薪资", "月薪", "奖金", "补贴"],
    "投资": ["理财", "基金", "股票", "债券", "收益", "分红", "利息"],
    "兼职": ["兼职", "外快", "项目", "佣金"],
}

# 收入关键词
INCOME_KEYWORDS = ["收入", "工资", "奖金", "退款", "转入", "收款", "红包", "分红", "收益", "利息"]


class ParsedTransaction:
    """解析后的交易记录"""
    def __init__(self, amount: Decimal, type: str, date: datetime, note: str, category_id: Optional[int] = None):
        self.amount = amount
        self.type = type  # 'income' or 'expense'
        self.date = date
        self.note = note
        self.category_id = category_id


class BillParser:
    """账单解析器 - 支持Alipay CSV, WeChat CSV, Excel"""
    
    def __init__(self, db_session):
        self.db = db_session
        self._load_categories()
    
    def _load_categories(self):
        """加载分类用于关键词匹配"""
        categories = self.db.query(Category).filter(Category.is_deleted == False).all()
        self.categories_map = {cat.name: cat.id for cat in categories}
        self.categories_type_map = {cat.name: cat.type for cat in categories}
    
    def parse(self, file_content: bytes, filename: str, file_type: str = None) -> List[ParsedTransaction]:
        """解析文件内容"""
        ext = Path(filename).suffix.lower()
        
        # 自动检测文件类型
        if file_type:
            pass
        elif ext in ['.xlsx', '.xls']:
            file_type = 'excel'
        else:
            # 尝试通过内容检测CSV类型
            file_type = self._detect_csv_type(file_content)
        
        if file_type == 'alipay_csv':
            return self._parse_alipay_csv(file_content)
        elif file_type == 'wechat_csv':
            return self._parse_wechat_csv(file_content)
        elif file_type == 'excel':
            return self._parse_excel(file_content)
        else:
            raise ValueError(f"不支持的文件格式: {file_type}")
    
    def _detect_csv_type(self, content: bytes) -> str:
        """通过内容检测CSV类型"""
        text = content.decode('utf-8-sig', errors='ignore')
        lines = text.split('\n')[:5]
        
        # Alipay CSV特征
        alipay_markers = ['支付宝', '交易对方', '商品说明', '商家实收']
        # WeChat CSV特征  
        wechat_markers = ['微信支付', '交易对方', '商品', '当前状态']
        
        text_content = '\n'.join(lines)
        
        if any(m in text_content for m in alipay_markers):
            return 'alipay_csv'
        elif any(m in text_content for m in wechat_markers):
            return 'wechat_csv'
        
        return 'unknown'
    
    def _parse_alipay_csv(self, content: bytes) -> List[ParsedTransaction]:
        """解析支付宝CSV"""
        transactions = []
        text = content.decode('utf-8-sig', errors='ignore')
        
        reader = csv.DictReader(io.StringIO(text))
        
        for row in reader:
            try:
                # 支付宝字段映射
                amount_str = row.get('金额', row.get('金额(元)', '')).strip()
                if not amount_str:
                    continue
                
                amount = abs(Decimal(amount_str))
                
                # 判断收支类型
                amount_field = row.get('金额', row.get('金额(元)', ''))
                is_income = '收入' in row.get('业务类型', '') or Decimal(amount_field) > 0
                
                # 日期解析
                date_str = row.get('创建时间', row.get('完成时间', '')).strip()
                if date_str:
                    date = self._parse_date(date_str)
                else:
                    continue
                
                # 备注
                note = row.get('商品说明', row.get('备注', '')).strip()
                
                # 自动分类
                category_id = self._auto_categorize(note, 'income' if is_income else 'expense')
                
                transactions.append(ParsedTransaction(
                    amount=amount,
                    type='income' if is_income else 'expense',
                    date=date,
                    note=note,
                    category_id=category_id
                ))
            except Exception:
                continue
        
        return transactions
    
    def _parse_wechat_csv(self, content: bytes) -> List[ParsedTransaction]:
        """解析微信CSV"""
        transactions = []
        text = content.decode('utf-8-sig', errors='ignore')
        
        reader = csv.DictReader(io.StringIO(text))
        
        for row in reader:
            try:
                # 微信字段映射
                amount_str = row.get('金额(元)', row.get('金额', '')).strip()
                if not amount_str:
                    continue
                
                amount = abs(Decimal(amount_str))
                
                # 判断收支类型
                is_income = row.get('交易类型', '') in ['收入', '转账', '红包'] or \
                           '收款' in row.get('交易状态', '')
                
                # 日期解析
                date_str = row.get('交易时间', '').strip()
                if date_str:
                    date = self._parse_date(date_str)
                else:
                    continue
                
                # 备注
                note = row.get('商品', row.get('备注', row.get('交易对方', ''))).strip()
                
                # 自动分类
                category_id = self._auto_categorize(note, 'income' if is_income else 'expense')
                
                transactions.append(ParsedTransaction(
                    amount=amount,
                    type='income' if is_income else 'expense',
                    date=date,
                    note=note,
                    category_id=category_id
                ))
            except Exception:
                continue
        
        return transactions
    
    def _parse_excel(self, content: bytes) -> List[ParsedTransaction]:
        """解析Excel文件"""
        transactions = []
        
        # 使用pandas读取
        df = pd.read_excel(io.BytesIO(content))
        
        # 尝试自动识别列
        columns = df.columns.tolist()
        
        # 寻找金额列
        amount_col = None
        for col in ['金额', '金额(元)', 'amount', 'Amount']:
            if col in columns:
                amount_col = col
                break
        
        # 寻找日期列
        date_col = None
        for col in ['日期', '交易日期', '时间', 'date', 'Date', '创建时间']:
            if col in columns:
                date_col = col
                break
        
        # 寻找备注列
        note_col = None
        for col in ['备注', '说明', '商品', '描述', 'note', 'Note', '商品说明']:
            if col in columns:
                note_col = col
                break
        
        if not amount_col or not date_col:
            raise ValueError("Excel文件缺少必要列(金额、日期)")
        
        for _, row in df.iterrows():
            try:
                amount_str = str(row[amount_col]).strip()
                if not amount_str or amount_str == 'nan':
                    continue
                
                amount = abs(Decimal(amount_str))
                
                # 判断收支类型（通过金额正负或类型列）
                is_income = Decimal(str(row[amount_col])) > 0
                
                # 日期解析
                date = self._parse_date(str(row[date_col]))
                
                # 备注
                note = str(row[note_col]) if note_col else ''
                if note == 'nan':
                    note = ''
                
                # 自动分类
                category_id = self._auto_categorize(note, 'income' if is_income else 'expense')
                
                transactions.append(ParsedTransaction(
                    amount=amount,
                    type='income' if is_income else 'expense',
                    date=date,
                    note=note,
                    category_id=category_id
                ))
            except Exception:
                continue
        
        return transactions
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        # 尝试多种格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日 %H:%M:%S',
            '%Y年%m月%d日',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # 默认返回今天
        return datetime.now()
    
    def _auto_categorize(self, note: str, trans_type: str) -> Optional[int]:
        """基于关键词自动分类"""
        if not note:
            return None
        
        note_lower = note.lower()
        
        # 首先尝试精确匹配分类名
        for cat_name, cat_id in self.categories_map.items():
            if cat_name in note:
                if self.categories_type_map.get(cat_name) == trans_type:
                    return cat_id
        
        # 然后尝试关键词匹配
        keywords = CATEGORY_KEYWORDS
        for cat_name, kw_list in keywords.items():
            if self.categories_type_map.get(cat_name) != trans_type:
                continue
            
            for kw in kw_list:
                if kw in note:
                    return self.categories_map.get(cat_name)
        
        return None
```

**Step 2: Update services __init__**

Modify: `app/services/__init__.py`

```python
from app.services.storage import storage_service
from app.services.bill_parser import BillParser, ParsedTransaction

__all__ = ["storage_service", "BillParser", "ParsedTransaction"]
```

---

## Task 5: Import Schemas

**Files:**
- Create: `app/schemas/import_record.py`

**Step 1: Create import schemas**

```python
# app/schemas/import_record.py
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
```

---

## Task 6: Import API

**Files:**
- Create: `app/api/imports.py`

**Step 1: Create import API**

```python
# app/api/imports.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.import_record import ImportRecord
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.import_record import (
    ImportRecordResponse,
    ImportPreviewResponse,
    ImportConfirmRequest,
    ImportConfirmResponse,
    ParsedTransactionSchema
)
from app.core.security import get_current_user
from app.models.user import User
from app.services.storage import storage_service
from app.services.bill_parser import BillParser
from app.core.config import settings
import hashlib

router = APIRouter()


@router.post("/upload", response_model=ImportRecordResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传文件"""
    # 验证文件类型
    ext = file.filename.split('.')[-1].lower() if file.filename else ''
    if f'.{ext}' not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {ext}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # 计算哈希
    file_hash = hashlib.sha256(content).hexdigest()
    
    # 检查是否已存在相同文件
    existing = db.query(ImportRecord).filter(
        ImportRecord.file_hash == file_hash,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if existing:
        # 返回现有记录
        existing.import_count += 1
        db.commit()
        db.refresh(existing)
        return existing
    
    # 保存文件
    file_path, file_hash = storage_service.save_file(current_user.id, content, file.filename)
    
    # 检测文件类型
    from app.services.bill_parser import BillParser
    parser = BillParser(db)
    file_type = parser._detect_csv_type(content)
    if file_type == 'unknown':
        ext = file.filename.split('.')[-1].lower()
        if ext in ['xlsx', 'xls']:
            file_type = 'excel'
    
    # 创建导入记录
    import_record = ImportRecord(
        file_name=file.filename,
        file_type=file_type,
        file_path=file_path,
        file_hash=file_hash,
        user_id=current_user.id,
        status='pending'
    )
    
    db.add(import_record)
    db.commit()
    db.refresh(import_record)
    
    return import_record


@router.get("/{import_id}/preview", response_model=ImportPreviewResponse)
def preview_import(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """预览导入数据"""
    import_record = db.query(ImportRecord).filter(
        ImportRecord.id == import_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not import_record:
        raise HTTPException(status_code=404, detail="导入记录不存在")
    
    # 获取文件内容
    content = storage_service.get_file(import_record.file_path)
    if not content:
        raise HTTPException(status_code=400, detail="文件内容读取失败")
    
    # 解析文件
    parser = BillParser(db)
    transactions = parser.parse(content, import_record.file_name, import_record.file_type)
    
    # 获取分类名称
    categories = {cat.id: cat.name for cat in db.query(Category).all()}
    
    # 构建预览数据
    parsed_transactions = []
    income_count = 0
    expense_count = 0
    
    for t in transactions:
        if t.type == 'income':
            income_count += 1
        else:
            expense_count += 1
        
        parsed_transactions.append(ParsedTransactionSchema(
            amount=t.amount,
            type=t.type,
            date=t.date,
            note=t.note,
            category_id=t.category_id,
            category_name=categories.get(t.category_id) if t.category_id else None
        ))
    
    # 更新状态
    import_record.status = 'parsed'
    db.commit()
    
    return ImportPreviewResponse(
        import_id=import_id,
        file_name=import_record.file_name,
        total_count=len(transactions),
        income_count=income_count,
        expense_count=expense_count,
        transactions=parsed_transactions
    )


@router.post("/{import_id}/confirm", response_model=ImportConfirmResponse)
def confirm_import(
    import_id: int,
    request: ImportConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认导入"""
    import_record = db.query(ImportRecord).filter(
        ImportRecord.id == import_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not import_record:
        raise HTTPException(status_code=404, detail="导入记录不存在")
    
    if import_record.status not in ['pending', 'parsed']:
        raise HTTPException(status_code=400, detail="该记录已处理")
    
    # 获取文件内容
    content = storage_service.get_file(import_record.file_path)
    if not content:
        raise HTTPException(status_code=400, detail="文件内容读取失败")
    
    # 解析文件
    parser = BillParser(db)
    transactions = parser.parse(content, import_record.file_name, import_record.file_type)
    
    # 应用分类映射覆盖
    if request.category_mapping:
        for t in transactions:
            if t.category_id in request.category_mapping:
                t.category_id = request.category_mapping[t.category_id]
    
    # 创建交易记录
    created_count = 0
    for t in transactions:
        # 如果没有自动分类，使用默认分类
        category_id = t.category_id
        if not category_id:
            # 使用对应类型的第一个分类
            default_cat = db.query(Category).filter(
                Category.type == t.type,
                Category.is_deleted == False
            ).first()
            category_id = default_cat.id if default_cat else None
        
        if not category_id:
            continue
        
        db_transaction = Transaction(
            amount=t.amount,
            type=t.type,
            category_id=category_id,
            date=t.date.date() if isinstance(t.date, datetime) else t.date,
            note=t.note,
            import_record_id=import_id
        )
        db.add(db_transaction)
        created_count += 1
    
    # 更新导入记录
    import_record.status = 'confirmed'
    import_record.import_count += 1
    import_record.import_count = created_count
    
    db.commit()
    db.refresh(import_record)
    
    return ImportConfirmResponse(
        import_id=import_id,
        created_count=created_count,
        import_record=import_record
    )


@router.get("/history", response_model=List[ImportRecordResponse])
def get_import_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取导入历史"""
    records = db.query(ImportRecord).filter(
        ImportRecord.user_id == current_user.id
    ).order_by(ImportRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return records
```

**Step 2: Update main.py to include imports router**

Modify: `app/main.py`

```python
from app.api import users, categories, transactions, budgets, tags, time_periods, recycle_bin, imports

# ... existing routers ...
app.include_router(imports.router, prefix="/api/imports", tags=["imports"])
```

---

## Task 7: Files API

**Files:**
- Create: `app/api/files.py`

**Step 1: Create files API**

```python
# app/api/files.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io

from app.db.database import get_db
from app.models.import_record import ImportRecord
from app.schemas.import_record import ImportRecordResponse
from app.core.security import get_current_user
from app.models.user import User
from app.services.storage import storage_service

router = APIRouter()


@router.get("/", response_model=List[ImportRecordResponse])
def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出用户的原始文件"""
    files = db.query(ImportRecord).filter(
        ImportRecord.user_id == current_user.id
    ).order_by(ImportRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return files


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载原始文件"""
    import_record = db.query(ImportRecord).filter(
        ImportRecord.id == file_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not import_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    content = storage_service.get_file(import_record.file_path)
    if not content:
        raise HTTPException(status_code=404, detail="文件内容不存在")
    
    # 确定content type
    ext = import_record.file_name.split('.')[-1].lower()
    media_type = 'text/csv' if ext == 'csv' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename="{import_record.file_name}"'
        }
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除原始文件"""
    import_record = db.query(ImportRecord).filter(
        ImportRecord.id == file_id,
        ImportRecord.user_id == current_user.id
    ).first()
    
    if not import_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除存储的文件
    storage_service.delete_file(import_record.file_path)
    
    # 删除数据库记录
    db.delete(import_record)
    db.commit()
    
    return None
```

**Step 2: Update main.py to include files router**

Modify: `app/main.py`

```python
from app.api import users, categories, transactions, budgets, tags, time_periods, recycle_bin, imports, files

# ... existing routers ...
app.include_router(files.router, prefix="/api/files", tags=["files"])
```

---

## Task 8: Frontend - API Service

**Files:**
- Create: `webui/src/services/imports.service.ts`

**Step 1: Create imports service**

```typescript
// webui/src/services/imports.service.ts
import apiClient from './api';
import type { ImportRecord, ImportPreview, ImportConfirmResponse } from '@/types';

export const importsService = {
  async uploadFile(file: File): Promise<ImportRecord> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<ImportRecord>('/imports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getPreview(importId: number): Promise<ImportPreview> {
    const response = await apiClient.get<ImportPreview>(`/imports/${importId}/preview`);
    return response.data;
  },

  async confirmImport(importId: number, categoryMapping?: Record<number, number>): Promise<ImportConfirmResponse> {
    const response = await apiClient.post<ImportConfirmResponse>(`/imports/${importId}/confirm`, {
      import_id: importId,
      category_mapping: categoryMapping,
    });
    return response.data;
  },

  async getHistory(skip = 0, limit = 20): Promise<ImportRecord[]> {
    const response = await apiClient.get<ImportRecord[]>('/imports/history', {
      params: { skip, limit },
    });
    return response.data;
  },

  async listFiles(skip = 0, limit = 20): Promise<ImportRecord[]> {
    const response = await apiClient.get<ImportRecord[]>('/files/', {
      params: { skip, limit },
    });
    return response.data;
  },

  async downloadFile(fileId: number): Promise<Blob> {
    const response = await apiClient.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async deleteFile(fileId: number): Promise<void> {
    await apiClient.delete(`/files/${fileId}`);
  },
};
```

---

## Task 9: Frontend - Types

**Files:**
- Modify: `webui/src/types/models.ts`

**Step 1: Add import types**

```typescript
// Add to webui/src/types/models.ts

export interface ImportRecord {
  id: number;
  file_name: string;
  file_type: string;
  file_path: string;
  file_hash: string;
  import_count: number;
  status: 'pending' | 'parsed' | 'confirmed' | 'failed';
  error_message?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface ParsedTransaction {
  amount: string | number;
  type: 'income' | 'expense';
  date: string;
  note: string;
  category_id?: number;
  category_name?: string;
}

export interface ImportPreview {
  import_id: number;
  file_name: string;
  total_count: number;
  income_count: number;
  expense_count: number;
  transactions: ParsedTransaction[];
}

export interface ImportConfirmResponse {
  import_id: number;
  created_count: number;
  import_record: ImportRecord;
}
```

---

## Task 10: Frontend - Store

**Files:**
- Create: `webui/src/stores/imports.ts`

**Step 1: Create imports store**

```typescript
// webui/src/stores/imports.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ImportRecord, ImportPreview, ParsedTransaction } from '@/types';
import { importsService } from '@/services/imports.service';

export const useImportsStore = defineStore('imports', () => {
  // State
  const currentImport = ref<ImportRecord | null>(null);
  const preview = ref<ImportPreview | null>(null);
  const history = ref<ImportRecord[]>([]);
  const files = ref<ImportRecord[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  async function uploadFile(file: File) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.uploadFile(file);
      currentImport.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to upload file';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPreview(importId: number) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.getPreview(importId);
      preview.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch preview';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function confirmImport(importId: number, categoryMapping?: Record<number, number>) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.confirmImport(importId, categoryMapping);
      preview.value = null;
      currentImport.value = null;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to confirm import';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchHistory(skip = 0, limit = 20) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.getHistory(skip, limit);
      history.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch history';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchFiles(skip = 0, limit = 20) {
    loading.value = true;
    error.value = null;
    try {
      const result = await importsService.listFiles(skip, limit);
      files.value = result;
      return result;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to fetch files';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function downloadFile(fileId: number) {
    try {
      const blob = await importsService.downloadFile(fileId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `import-${fileId}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download file:', err);
      throw err;
    }
  }

  async function deleteFile(fileId: number) {
    loading.value = true;
    error.value = null;
    try {
      await importsService.deleteFile(fileId);
      files.value = files.value.filter(f => f.id !== fileId);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Failed to delete file';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function clearPreview() {
    preview.value = null;
    currentImport.value = null;
  }

  return {
    currentImport,
    preview,
    history,
    files,
    loading,
    error,
    uploadFile,
    fetchPreview,
    confirmImport,
    fetchHistory,
    fetchFiles,
    downloadFile,
    deleteFile,
    clearPreview,
  };
});
```

---

## Task 11: Frontend - ImportView

**Files:**
- Create: `webui/src/views/ImportView.vue`

**Step 1: Create ImportView**

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useImportsStore } from '@/stores/imports';
import { useCategoriesStore } from '@/stores/categories';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';

const { t } = useI18n();
const importsStore = useImportsStore();
const categoriesStore = useCategoriesStore();
const authStore = useAuthStore();

const isDragging = ref(false);
const selectedFile = ref<File | null>(null);
const activeTab = ref<'upload' | 'preview' | 'history' | 'files'>('upload');

onMounted(async () => {
  authStore.checkAuth();
  await categoriesStore.fetchCategories();
  await importsStore.fetchHistory();
  await importsStore.fetchFiles();
});

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFileSelect(files[0]);
  }
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0]);
  }
}

async function handleFileSelect(file: File) {
  const allowedTypes = ['.csv', '.xlsx', '.xls'];
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  
  if (!allowedTypes.includes(ext)) {
    alert(t('import.invalidFileType'));
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) {
    alert(t('import.fileTooLarge'));
    return;
  }
  
  selectedFile.value = file;
  
  try {
    const importRecord = await importsStore.uploadFile(file);
    await importsStore.fetchPreview(importRecord.id);
    activeTab.value = 'preview';
  } catch (error) {
    console.error('Upload failed:', error);
  }
}

async function handleConfirm() {
  if (!importsStore.currentImport) return;
  
  try {
    await importsStore.confirmImport(importsStore.currentImport.id);
    selectedFile.value = null;
    await importsStore.fetchHistory();
    activeTab.value = 'history';
  } catch (error) {
    console.error('Confirm failed:', error);
  }
}

function handleCancel() {
  importsStore.clearPreview();
  selectedFile.value = null;
  activeTab.value = 'upload';
}

async function handleDownload(fileId: number) {
  await importsStore.downloadFile(fileId);
}

async function handleDeleteFile(fileId: number) {
  if (confirm(t('import.confirmDeleteFile'))) {
    await importsStore.deleteFile(fileId);
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString();
}

function formatAmount(amount: string | number): string {
  return new Number(amount).toFixed(2);
}

const expenseCategories = computed(() => categoriesStore.expenseCategories);
const incomeCategories = computed(() => categoriesStore.incomeCategories);
</script>

<template>
  <div class="import-view">
    <!-- Header -->
    <div class="header">
      <h1 class="header__title">{{ t('import.title') }}</h1>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'upload' }"
        @click="activeTab = 'upload'"
      >
        {{ t('import.upload') }}
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'preview' }"
        @click="activeTab = 'preview'"
        :disabled="!importsStore.preview"
      >
        {{ t('import.preview') }}
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        {{ t('import.history') }}
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'files' }"
        @click="activeTab = 'files'"
      >
        {{ t('import.files') }}
      </button>
    </div>

    <!-- Upload Tab -->
    <div v-if="activeTab === 'upload'" class="tab-content">
      <div 
        class="drop-zone"
        :class="{ 'drop-zone--active': isDragging }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <div class="drop-zone__icon">📁</div>
        <p class="drop-zone__text">{{ t('import.dropzoneText') }}</p>
        <p class="drop-zone__subtext">{{ t('import.dropzoneSubtext') }}</p>
        <input 
          type="file" 
          class="drop-zone__input"
          accept=".csv,.xlsx,.xls"
          @change="handleFileInput"
        />
        <Button variant="secondary" @click="($event.target as HTMLInputElement)?.closest('.drop-zone')?.querySelector('.drop-zone__input')?.click()">
          {{ t('import.selectFile') }}
        </Button>
      </div>

      <!-- Selected File -->
      <div v-if="selectedFile" class="selected-file">
        <p>{{ selectedFile.name }}</p>
        <p class="file-size">{{ (selectedFile.size / 1024).toFixed(2) }} KB</p>
      </div>
    </div>

    <!-- Preview Tab -->
    <div v-if="activeTab === 'preview' && importsStore.preview" class="tab-content">
      <div class="preview-header">
        <h2>{{ importsStore.preview.file_name }}</h2>
        <div class="preview-stats">
          <span class="stat">{{ t('import.total') }}: {{ importsStore.preview.total_count }}</span>
          <span class="stat stat--income">{{ t('import.income') }}: {{ importsStore.preview.income_count }}</span>
          <span class="stat stat--expense">{{ t('import.expense') }}: {{ importsStore.preview.expense_count }}</span>
        </div>
      </div>

      <div class="preview-table">
        <table>
          <thead>
            <tr>
              <th>{{ t('import.date') }}</th>
              <th>{{ t('import.type') }}</th>
              <th>{{ t('import.amount') }}</th>
              <th>{{ t('import.category') }}</th>
              <th>{{ t('import.note') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(tx, idx) in importsStore.preview.transactions" :key="idx">
              <td>{{ formatDate(tx.date) }}</td>
              <td>
                <span :class="['type-badge', `type-badge--${tx.type}`]">
                  {{ t(`transaction.${tx.type}`) }}
                </span>
              </td>
              <td :class="['amount', `amount--${tx.type}`]">
                {{ tx.type === 'expense' ? '-' : '+' }}{{ formatAmount(tx.amount) }}
              </td>
              <td>{{ tx.category_name || '-' }}</td>
              <td class="note">{{ tx.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="preview-actions">
        <Button variant="secondary" @click="handleCancel">{{ t('common.cancel') }}</Button>
        <Button variant="primary" @click="handleConfirm">{{ t('import.confirm') }}</Button>
      </div>
    </div>

    <!-- History Tab -->
    <div v-if="activeTab === 'history'" class="tab-content">
      <div v-if="importsStore.history.length === 0" class="empty-state">
        <p>{{ t('import.noHistory') }}</p>
      </div>
      <div v-else class="history-list">
        <div v-for="record in importsStore.history" :key="record.id" class="history-item">
          <div class="history-info">
            <span class="file-name">{{ record.file_name }}</span>
            <span class="file-date">{{ formatDate(record.created_at) }}</span>
          </div>
          <div class="history-stats">
            <span class="status" :class="`status--${record.status}`">{{ record.status }}</span>
            <span class="count">{{ record.import_count }} {{ t('import.records') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Files Tab -->
    <div v-if="activeTab === 'files'" class="tab-content">
      <div v-if="importsStore.files.length === 0" class="empty-state">
        <p>{{ t('import.noFiles') }}</p>
      </div>
      <div v-else class="files-list">
        <div v-for="file in importsStore.files" :key="file.id" class="file-item">
          <div class="file-info">
            <span class="file-name">{{ file.file_name }}</span>
            <span class="file-date">{{ formatDate(file.created_at) }}</span>
          </div>
          <div class="file-actions">
            <Button variant="secondary" size="small" @click="handleDownload(file.id)">
              {{ t('import.download') }}
            </Button>
            <Button variant="tertiary" size="small" @click="handleDeleteFile(file.id)">
              {{ t('import.delete') }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.import-view {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.header {
  padding: var(--space-6);
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
}

.header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.tabs {
  display: flex;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-separator);
  padding: 0 var(--space-4);
}

.tab {
  padding: var(--space-3) var(--space-4);
  border: none;
  background: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--duration-fast);
}

.tab:hover:not(:disabled) {
  color: var(--color-text-primary);
}

.tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-content {
  padding: var(--space-6);
}

.drop-zone {
  border: 2px dashed var(--color-separator);
  border-radius: var(--radius-lg);
  padding: var(--space-12);
  text-align: center;
  position: relative;
  transition: all var(--duration-fast);
  cursor: pointer;
}

.drop-zone:hover,
.drop-zone--active {
  border-color: var(--color-primary);
  background: var(--color-bg-primary);
}

.drop-zone__icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
}

.drop-zone__text {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.drop-zone__subtext {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-4);
}

.drop-zone__input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.selected-file {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.file-size {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.preview-header {
  margin-bottom: var(--space-4);
}

.preview-stats {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-2);
}

.stat {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stat--income {
  color: var(--color-success);
}

.stat--expense {
  color: var(--color-error);
}

.preview-table {
  overflow-x: auto;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.preview-table th,
.preview-table td {
  padding: var(--space-3);
  text-align: left;
  border-bottom: 1px solid var(--color-separator);
}

.preview-table th {
  background: var(--color-bg-secondary);
  font-weight: var(--font-weight-semibold);
}

.amount--income {
  color: var(--color-success);
}

.amount--expense {
  color: var(--color-error);
}

.note {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.type-badge--income {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.type-badge--expense {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.empty-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-secondary);
}

.history-list,
.files-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.history-item,
.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.file-name {
  font-weight: var(--font-weight-medium);
}

.file-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.history-stats,
.file-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.status {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.status--confirmed {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status--pending,
.status--parsed {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.status--failed {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}
</style>
```

---

## Task 12: Update Navigation

**Files:**
- Modify: `webui/src/App.vue`

**Step 1: Add import to navigation**

Add to navItems:
```typescript
{ path: '/import', name: t('nav.import'), icon: '📥' },
```

**Step 2: Update router**

Modify: `webui/src/router/index.ts`

Add:
```typescript
import ImportView from '@/views/ImportView.vue'

// Add route:
{
  path: '/import',
  name: 'import',
  component: ImportView,
  meta: { requiresAuth: true }
},
```

---

## Task 13: Add i18n Translations

**Files:**
- Find and modify: `webui/src/locales/*.json`

**Step 1: Add translations**

Add to zh-CN and en files:
```json
{
  "import": {
    "title": "导入",
    "upload": "上传",
    "preview": "预览",
    "history": "历史",
    "files": "文件管理",
    "dropzoneText": "拖拽文件到此处或点击选择",
    "dropzoneSubtext": "支持 CSV、Excel 文件",
    "selectFile": "选择文件",
    "invalidFileType": "不支持的文件类型",
    "fileTooLarge": "文件超过10MB限制",
    "total": "总计",
    "income": "收入",
    "expense": "支出",
    "date": "日期",
    "type": "类型",
    "amount": "金额",
    "category": "分类",
    "note": "备注",
    "confirm": "确认导入",
    "confirmDeleteFile": "确定删除此文件？",
    "download": "下载",
    "delete": "删除",
    "noHistory": "暂无导入记录",
    "noFiles": "暂无文件",
    "records": "条记录"
  },
  "nav": {
    "import": "导入"
  }
}
```

---

## Task 14: Test and Verify

**Step 1: Run database migration**

```bash
python -c "from app.db.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
```

**Step 2: Start backend**

```bash
python -m uvicorn app.main:app --reload
```

**Step 3: Test upload endpoint**

```bash
# Create test CSV file
echo "交易对方,商品说明,金额,创建时间,业务类型" > test_alipay.csv
echo "淘宝,购买商品,100.00,2024-01-01 12:00:00,购物" >> test_alipay.csv

# Test upload
curl -X POST -F "file=@test_alipay.csv" http://localhost:8000/api/imports/upload -H "Authorization: Bearer YOUR_TOKEN"
```

**Step 4: Verify with frontend**

```bash
cd webui && npm run dev
```

Navigate to /import and test the full flow.

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Add Python dependencies |
| 2 | ImportRecord model |
| 3 | Storage service |
| 4 | Bill parser service |
| 5 | Import schemas |
| 6 | Import API endpoints |
| 7 | Files API endpoints |
| 8 | Frontend API service |
| 9 | Frontend types |
| 10 | Frontend store |
| 11 | ImportView component |
| 12 | Navigation & routing |
| 13 | i18n translations |
| 14 | Test and verify |

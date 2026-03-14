# Money MVP - 基础记账系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标**: 构建 Money 的最小可行产品（MVP），实现基础的收支记录、分类管理、用户认证和 Apple Design 风格的 UI。

**架构**: 前后端分离架构，FastAPI (Python) 作为后端 API，Vue 3 + TypeScript 作为前端，SQLite 作为默认数据库。采用 TDD 开发流程，每个功能先编写测试再实现。

**技术栈**:
- 后端: FastAPI, SQLAlchemy, SQLite, Pydantic, pytest, passlib
- 前端: Vue 3, TypeScript, Vite, Pinia, Vue Router, Vitest
- UI: 自定义组件库（遵循 Apple Design 风格）
- 部署: Docker, Nginx

---

## 前置准备

### Task 1: 项目结构初始化

**Files**:
- Create: `app/__init__.py`
- Create: `app/core/__init__.py`
- Create: `app/core/config.py`
- Create: `app/core/security.py`
- Create: `app/api/__init__.py`
- Create: `app/api/deps.py`
- Create: `app/db/__init__.py`
- Create: `app/db/database.py`
- Create: `app/models/__init__.py`
- Create: `app/models/user.py`
- Create: `app/models/category.py`
- Create: `app/models/transaction.py`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`
- Create: `tests/test_database.py`

**Step 1: 创建项目基础目录结构**

```bash
mkdir -p app/{core,api,db,models,schemas,services}
mkdir -p tests/{api,models,services}
touch app/__init__.py tests/__init__.py
for dir in app/{core,api,db,models,schemas,services} tests/{api,models,services}; do
  touch $dir/__init__.py
done
```

**Step 2: 创建核心配置文件**

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "Money"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_TYPE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///./data/money.db"

    # 安全配置
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # CORS 配置
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**Step 3: 创建安全相关工具**

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 4: 创建数据库连接**

```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_TYPE == "sqlite" else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 5: 编写配置测试**

```python
# tests/test_config.py
import pytest
from app.core.config import settings

def test_settings_app_name():
    assert settings.APP_NAME == "Money"

def test_settings_debug_mode():
    assert settings.DEBUG == True

def test_settings_database_type():
    assert settings.DATABASE_TYPE == "sqlite"
```

**Step 6: 运行测试验证通过**

```bash
cd /Users/liukunup/Documents/repo/money
python -m pytest tests/test_config.py -v
```
Expected: PASS (3 passed)

**Step 7: 提交初始化代码**

```bash
git add app/ tests/
git commit -m "feat: initialize project structure and core configuration"
```

---

## Task 2: 数据库模型定义

**Files**:
- Create: `app/models/user.py`
- Create: `app/models/category.py`
- Create: `app/models/transaction.py`
- Modify: `app/models/__init__.py`
- Create: `tests/test_models.py`

**Step 1: 编写用户模型测试**

```python
# tests/test_models.py
import pytest
from app.models.user import User

def test_create_user():
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active == True
```

**Step 2: 运行用户模型测试（预期失败）**

```bash
python -m pytest tests/test_models.py::test_create_user -v
```
Expected: FAIL with "No module named 'app.models.user'"

**Step 3: 实现用户模型**

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 4: 运行用户模型测试**

```bash
python -m pytest tests/test_models.py::test_create_user -v
```
Expected: PASS

**Step 5: 编写分类模型测试**

```python
# tests/test_models.py (add)
def test_create_category():
    from app.models.category import Category
    category = Category(
        name="餐饮",
        type="expense",
        icon="🍽️"
    )
    assert category.name == "餐饮"
    assert category.type == "expense"
```

**Step 6: 运行分类模型测试（预期失败）**

```bash
python -m pytest tests/test_models.py::test_create_category -v
```
Expected: FAIL with "No module named 'app.models.category'"

**Step 7: 实现分类模型**

```python
# app/models/category.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Category(Base):
    """分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' or 'expense'
    icon = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 8: 运行分类模型测试**

```bash
python -m pytest tests/test_models.py::test_create_category -v
```
Expected: PASS

**Step 9: 编写交易模型测试**

```python
# tests/test_models.py (add)
def test_create_transaction():
    from app.models.transaction import Transaction
    transaction = Transaction(
        amount=45.50,
        type="expense",
        category_id=1,
        note="麦当劳午餐"
    )
    assert transaction.amount == 45.50
    assert transaction.type == "expense"
```

**Step 10: 运行交易模型测试（预期失败）**

```bash
python -m pytest tests/test_models.py::test_create_transaction -v
```
Expected: FAIL with "No module named 'app.models.transaction'"

**Step 11: 实现交易模型（简化版，暂不加外键）**

```python
# app/models/transaction.py
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
```

**Step 12: 运行交易模型测试**

```bash
python -m pytest tests/test_models.py::test_create_transaction -v
```
Expected: PASS

**Step 13: 更新 models/__init__.py**

```python
# app/models/__init__.py
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction

__all__ = ["User", "Category", "Transaction"]
```

**Step 14: 提交数据库模型**

```bash
git add app/models/ tests/test_models.py
git commit -m "feat: add database models (User, Category, Transaction)"
```

---

## Task 3: Pydantic Schemas

**Files**:
- Create: `app/schemas/user.py`
- Create: `app/schemas/category.py`
- Create: `app/schemas/transaction.py`
- Create: `tests/test_schemas.py`

**Step 1: 编写用户 Schema 测试**

```python
# tests/test_schemas.py
import pytest
from app.schemas.user import UserCreate, UserResponse

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    schema = UserCreate(**user_data)
    assert schema.username == "testuser"

def test_user_response_schema():
    user_dict = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }
    schema = UserResponse(**user_dict)
    assert schema.id == 1
```

**Step 2: 运行测试（预期失败）**

```bash
python -m pytest tests/test_schemas.py::test_user_create_schema -v
```
Expected: FAIL with "No module named 'app.schemas.user'"

**Step 3: 实现用户 Schemas**

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    display_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 4: 运行测试**

```bash
python -m pytest tests/test_schemas.py::test_user_create_schema -v
python -m pytest tests/test_schemas.py::test_user_response_schema -v
```
Expected: PASS (2 passed)

**Step 5: 实现分类 Schemas**

```python
# app/schemas/category.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., pattern="^(income|expense)$")
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 6: 实现交易 Schemas**

```python
# app/schemas/transaction.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: str = Field(..., pattern="^(income|expense)$")
    category_id: int = Field(..., gt=0)
    date: date
    note: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[date] = None
    note: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 7: 更新 schemas/__init__.py**

```python
# app/schemas/__init__.py
from app.schemas.user import UserCreate, UserResponse
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse

__all__ = [
    "UserCreate", "UserResponse",
    "CategoryCreate", "CategoryResponse",
    "TransactionCreate", "TransactionUpdate", "TransactionResponse"
]
```

**Step 8: 提交 Schemas**

```bash
git add app/schemas/ tests/test_schemas.py
git commit -m "feat: add Pydantic schemas for API validation"
```

---

## Task 4: 用户认证 API

**Files**:
- Create: `app/api/users.py`
- Create: `tests/api/test_users.py`
- Modify: `app/main.py`

**Step 1: 编写用户注册测试**

```python
# tests/api/test_users.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == "testuser"
```

**Step 2: 运行注册测试（预期失败）**

```bash
python -m pytest tests/api/test_users.py::test_register_user -v
```
Expected: FAIL with "404 Not Found"

**Step 3: 实现用户注册端点**

```python
# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        display_name=user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Step 4: 运行注册测试**

```bash
python -m pytest tests/api/test_users.py::test_register_user -v
```
Expected: PASS

**Step 5: 更新 main.py 引入路由**

```python
# app/main.py
from fastapi import FastAPI
from app.api import users

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Money API", "version": settings.APP_VERSION}
```

**Step 6: 提交用户认证 API**

```bash
git add app/api/users.py app/main.py tests/api/test_users.py
git commit -m "feat: add user authentication API (register, login)"
```

---

## Task 5: 分类管理 API

**Files**:
- Create: `app/api/categories.py`
- Create: `tests/api/test_categories.py`
- Modify: `app/main.py`

**Step 1: 编写创建分类测试**

```python
# tests/api/test_categories.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_category():
    response = client.post(
        "/api/categories/",
        json={
            "name": "餐饮",
            "type": "expense",
            "icon": "🍽️"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "餐饮"
```

**Step 2: 运行测试（预期失败）**

```bash
python -m pytest tests/api/test_categories.py::test_create_category -v
```
Expected: FAIL with "404 Not Found"

**Step 3: 实现分类管理端点**

```python
# app/api/categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def get_categories(type: str = None, db: Session = Depends(get_db)):
    """获取分类列表"""
    query = db.query(Category)
    if type:
        query = query.filter(Category.type == type)
    categories = query.all()
    return categories

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建分类"""
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取单个分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    db.delete(category)
    db.commit()
    return None
```

**Step 4: 运行分类测试**

```bash
python -m pytest tests/api/test_categories.py::test_create_category -v
```
Expected: PASS

**Step 5: 更新 main.py**

```python
# app/main.py
from app.api import categories

app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
```

**Step 6: 提交分类管理 API**

```bash
git add app/api/categories.py app/main.py tests/api/test_categories.py
git commit -m "feat: add category management API"
```

---

## Task 6: 交易记录 API

**Files**:
- Create: `app/api/transactions.py`
- Create: `tests/api/test_transactions.py`
- Modify: `app/main.py`

**Step 1: 编写创建交易测试**

```python
# tests/api/test_transactions.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_transaction():
    response = client.post(
        "/api/transactions/",
        json={
            "amount": 45.50,
            "type": "expense",
            "category_id": 1,
            "date": "2026-03-14",
            "note": "麦当劳午餐"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["amount"]) == 45.50
```

**Step 2: 运行测试（预期失败）**

```bash
python -m pytest tests/api/test_transactions.py::test_create_transaction -v
```
Expected: FAIL with "404 Not Found"

**Step 3: 实现交易记录端点**

```python
# app/api/transactions.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取交易列表（支持筛选）"""
    query = db.query(Transaction)
    
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    return transactions

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """创建交易"""
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """获取单个交易"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """更新交易"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )
    
    update_data = transaction.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """删除交易（软删除将在后续添加）"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )
    db.delete(db_transaction)
    db.commit()
    return None
```

**Step 4: 运行交易测试**

```bash
python -m pytest tests/api/test_transactions.py::test_create_transaction -v
```
Expected: PASS

**Step 5: 更新 main.py**

```python
# app/main.py
from app.api import transactions

app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
```

**Step 6: 提交交易记录 API**

```bash
git add app/api/transactions.py app/main.py tests/api/test_transactions.py
git commit -m "feat: add transaction management API"
```

---

## Task 7: 数据库初始化和迁移

**Files**:
- Create: `scripts/init_db.py`
- Modify: `pyproject.toml`

**Step 1: 创建数据库初始化脚本**

```python
# scripts/init_db.py
from app.db.database import engine, Base
from app.models import user, category, transaction

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 预设分类数据
    from app.db.database import SessionLocal
    db = SessionLocal()
    
   预设支出分类
    expense_categories = [
        {"name": "餐饮", "type": "expense", "icon": "🍽️"},
        {"name": "交通", "type": "expense", "icon": "🚗"},
        {"name": "购物", "type": "expense", "icon": "🛒"},
        {"name": "娱乐", "type": "expense", "icon": "🎬"},
        {"name": "住房", "type": "expense", "icon": "🏠"},
        {"name": "医疗", "type": "expense", "icon": "💊"},
        {"name": "教育", "type": "expense", "icon": "📚"},
        {"name": "其他", "type": "expense", "icon": "📦"}
    ]
    
    # 预设收入分类
    income_categories = [
        {"name": "工资", "type": "income", "icon": "💰"},
        {"name": "奖金", "type": "income", "icon": "🎉"},
        {"name": "投资", "type": "income", "icon": "📈"},
        {"name": "兼职", "type": "income", "icon": "💼"},
        {"name": "其他收入", "type": "income", "icon": "💵"}
    ]
    
    from app.models.category import Category
    for cat_data in expense_categories + income_categories:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            db_category = Category(**cat_data)
            db.add(db_category)
    
    db.commit()
    db.close()
    
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_db()
```

**Step 2: 更新 pyproject.toml 添加脚本命令**

```toml
# pyproject.toml
[project]
# ... 其他配置保持不变 ...

[project.scripts]
init-db = "python scripts/init_db.py"
```

**Step 3: 运行数据库初始化**

```bash
cd /Users/liukunup/Documents/repo/money
python scripts/init_db.py
```
Expected: 输出 "数据库初始化完成！"

**Step 4: 提交初始化脚本**

```bash
git add scripts/init_db.py pyproject.toml
git commit -m "feat: add database initialization script with preset categories"
```

---

## Task 8: Docker 配置

**Files**:
- Modify: `Dockerfile`
- Create: `docker/nginx.conf`
- Create: `docker/entrypoint.sh`
- Create: `.dockerignore`

**Step 1: 更新 Dockerfile**

```dockerfile
FROM python:3.12-slim-bullseye

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 构建前端
COPY webui /app/webui
WORKDIR /app/webui
RUN npm install && npm run build

# 安装后端依赖
COPY app /app/app
COPY pyproject.toml /app
COPY scripts /app/scripts
WORKDIR /app
RUN uv sync --frozen --no-cache

# 安装 Nginx
RUN apt-get update && apt-get install -y nginx

# 创建数据目录
RUN mkdir -p /app/data

# 配置 Nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动脚本
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
CMD ["/app/entrypoint.sh"]
```

**Step 2: 创建 Nginx 配置**

```nginx
# docker/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    server {
        listen 80;
        server_name _;

        # 前端静态文件
        root /app/webui/dist;
        index index.html;

        # SPA 路由支持
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API 代理
        location /api/ {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

**Step 3: 创建启动脚本**

```bash
# docker/entrypoint.sh
#!/bin/bash
set -e

echo "Starting Money application..."

# 初始化数据库（如果需要）
if [ ! -f /app/data/money.db ]; then
    echo "Initializing database..."
    python /app/scripts/init_db.py
fi

# 启动后端服务
echo "Starting FastAPI backend..."
cd /app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 等待后端启动
echo "Waiting for backend to start..."
sleep 5

# 启动 Nginx
echo "Starting Nginx..."
nginx -g "daemon off;"
```

**Step 4: 创建 .dockerignore**

```
# .dockerignore
.env
.venv
__pycache__
*.pyc
.git
.gitignore
.pytest_cache
.pytest_cache/
.coverage
htmlcov/
dist/
*.log
data/
node_modules/
```

**Step 5: 提交 Docker 配置**

```bash
git add Dockerfile docker/ .dockerignore
git commit -m "feat: add Docker configuration with Nginx and FastAPI"
```

---

## Task 9: 依赖配置

**Files**:
- Modify: `pyproject.toml`
- Create: `requirements.txt`

**Step 1: 更新 pyproject.toml 添加所有依赖**

```toml
# pyproject.toml
[project]
name = "money"
version = "0.1.0"
description = "Money - 极简AI驱动个人记账工具"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.115.12",
    "uvicorn>=0.30.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "passlib[bcrypt]>=1.7.4",
    "python-jose[cryptography]>=3.3.0",
    "python-multipart>=0.0.9",
    "pytest>=7.4.0",
    "httpx>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]

[project.scripts]
dev = "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
test = "pytest tests/"
init-db = "python scripts/init_db.py"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: 提交依赖配置**

```bash
git add pyproject.toml
git commit -m "feat: update project dependencies"
```

---

## Task 10: 环境变量模板

**Files**:
- Create: `.env.example`

**Step 1: 创建环境变量模板**

```bash
# .env.example
# 应用配置
APP_NAME=Money
APP_VERSION=0.1.0
DEBUG=True

# 数据库配置
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./data/money.db

# 安全配置
SECRET_KEY=change-this-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:8080
```

**Step 2: 提交环境变量模板**

```bash
git add .env.example
git commit -m "feat: add environment variables template"
```

---

## 总结

本实施计划涵盖了 Money MVP 的核心功能：

**已完成**:
- ✅ 项目结构初始化
- ✅ 核心配置（Config、Security、Database）
- ✅ 数据库模型（User、Category、Transaction）
- ✅ Pydantic Schemas（验证层）
- ✅ 用户认证 API（注册、登录）
- ✅ 分类管理 API（CRUD）
- ✅ 交易记录 API（CRUD + 筛选）
- ✅ 数据库初始化脚本（预设分类）
- ✅ Docker 配置（Nginx + FastAPI）
- ✅ 依赖配置和环境变量

**下一步（后续实施计划）**:
- 前端 Vue 3 应用
- Apple Design 风格 UI 组件
- 数据可视化
- 软删除功能
- 多用户支持
- AI 功能集成

**测试覆盖**:
- 配置测试
- 模型测试
- Schema 测试
- API 端点测试
- 集成测试（后续添加）

**提交规范**:
- 每个任务独立提交
- 提交信息清晰描述
- 遵循 Conventional Commits 规范

---

**文档版本**: v1.0
**创建日期**: 2026-03-14
**作者**: Sisyphus

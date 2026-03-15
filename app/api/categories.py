from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryResponse
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    type: str = None,
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    query = db.query(Category)
    
    if not include_deleted:
        query = query.filter(Category.is_deleted == False)
    
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
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """软删除分类"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    category.is_deleted = True
    category.deleted_at = datetime.utcnow()
    category.deleted_by = current_user.id
    
    db.commit()
    return None

@router.post("/{category_id}/restore", response_model=CategoryResponse)
def restore_category(category_id: int, db: Session = Depends(get_db)):
    """恢复已删除的分类"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == True
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在或未被删除"
        )

    category.is_deleted = False
    category.deleted_at = None
    category.deleted_by = None
    
    db.commit()
    db.refresh(category)
    return category

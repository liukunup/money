from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.db.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.tag import Tag
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

# Response schemas for recycle bin items
class DeletedItem(BaseModel):
    id: int
    type: str  # 'transaction', 'category', 'tag'
    item_id: int
    item_type: str  # 'income' or 'expense' for transactions/categories
    name: str  # Human-readable name
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

class RecycleBinStats(BaseModel):
    total_transactions: int
    total_categories: int
    total_tags: int

@router.get("/", response_model=List[DeletedItem])
def get_recycle_bin(
    item_type: Optional[str] = Query(None, description="Filter by type: transaction, category, tag"),
    db: Session = Depends(get_db)
):
    """获取回收站中的所有删除项目"""
    items: List[DeletedItem] = []
    
    # Get deleted transactions
    if item_type is None or item_type == 'transaction':
        transactions = db.query(Transaction).filter(
            Transaction.is_deleted == True
        ).order_by(Transaction.deleted_at.desc()).all()
        
        for t in transactions:
            items.append(DeletedItem(
                id=t.id,
                type='transaction',
                item_id=t.id,
                item_type=t.type,
                name=f"{t.type}: {t.amount} - {t.note or 'No note'}",
                deleted_at=t.deleted_at,
                deleted_by=t.deleted_by
            ))
    
    # Get deleted categories
    if item_type is None or item_type == 'category':
        categories = db.query(Category).filter(
            Category.is_deleted == True
        ).order_by(Category.deleted_at.desc()).all()
        
        for c in categories:
            items.append(DeletedItem(
                id=c.id,
                type='category',
                item_id=c.id,
                item_type=c.type,
                name=f"{c.type}: {c.name}",
                deleted_at=c.deleted_at,
                deleted_by=c.deleted_by
            ))
    
    # Get deleted tags
    if item_type is None or item_type == 'tag':
        tags = db.query(Tag).filter(
            Tag.is_deleted == True
        ).order_by(Tag.deleted_at.desc()).all()
        
        for t in tags:
            items.append(DeletedItem(
                id=t.id,
                type='tag',
                item_id=t.id,
                item_type=t.type or 'general',
                name=t.name,
                deleted_at=t.deleted_at,
                deleted_by=None
            ))
    
    return items

@router.get("/stats", response_model=RecycleBinStats)
def get_recycle_bin_stats(db: Session = Depends(get_db)):
    """获取回收站统计"""
    stats = RecycleBinStats(
        total_transactions=db.query(Transaction).filter(Transaction.is_deleted == True).count(),
        total_categories=db.query(Category).filter(Category.is_deleted == True).count(),
        total_tags=db.query(Tag).filter(Tag.is_deleted == True).count()
    )
    return stats

@router.post("/transactions/{transaction_id}/restore", response_model=dict)
def restore_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """恢复交易"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == True
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在或未被删除"
        )

    transaction.is_deleted = False
    transaction.deleted_at = None
    transaction.deleted_by = None
    
    db.commit()
    return {"message": "交易已恢复", "id": transaction_id}

@router.post("/categories/{category_id}/restore", response_model=dict)
def restore_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """恢复分类"""
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
    return {"message": "分类已恢复", "id": category_id}

@router.post("/tags/{tag_id}/restore", response_model=dict)
def restore_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """恢复标签"""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.is_deleted == True
    ).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在或未被删除"
        )

    tag.is_deleted = False
    tag.deleted_at = None
    
    db.commit()
    return {"message": "标签已恢复", "id": tag_id}

@router.delete("/transactions/{transaction_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """永久删除交易"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == True
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在或未被删除"
        )

    db.delete(transaction)
    db.commit()
    return None

@router.delete("/categories/{category_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """永久删除分类"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == True
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在或未被删除"
        )

    db.delete(category)
    db.commit()
    return None

@router.delete("/tags/{tag_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """永久删除标签"""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.is_deleted == True
    ).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在或未被删除"
        )

    db.delete(tag)
    db.commit()
    return None

@router.delete("/empty", status_code=status.HTTP_204_NO_CONTENT)
def empty_recycle_bin(
    days: int = Query(30, description="永久删除N天前的数据"),
    db: Session = Depends(get_db)
):
    """清空回收站（删除N天前的数据）"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Delete old transactions
    db.query(Transaction).filter(
        Transaction.is_deleted == True,
        Transaction.deleted_at < cutoff_date
    ).delete()
    
    # Delete old categories
    db.query(Category).filter(
        Category.is_deleted == True,
        Category.deleted_at < cutoff_date
    ).delete()
    
    # Delete old tags
    db.query(Tag).filter(
        Tag.is_deleted == True,
        Tag.deleted_at < cutoff_date
    ).delete()
    
    db.commit()
    return None

@router.delete("/empty-all", status_code=status.HTTP_204_NO_CONTENT)
def empty_recycle_bin_all(db: Session = Depends(get_db)):
    """清空回收站（删除所有数据）"""
    
    # Delete all soft-deleted transactions
    db.query(Transaction).filter(
        Transaction.is_deleted == True
    ).delete()
    
    # Delete all soft-deleted categories
    db.query(Category).filter(
        Category.is_deleted == True
    ).delete()
    
    # Delete all soft-deleted tags
    db.query(Tag).filter(
        Tag.is_deleted == True
    ).delete()
    
    db.commit()
    return None

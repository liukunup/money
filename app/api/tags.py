from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter()

@router.get("/", response_model=List[TagResponse])
def get_tags(
    type: Optional[str] = None,
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    query = db.query(Tag)
    
    if not include_deleted:
        query = query.filter(Tag.is_deleted == False)
    
    if type:
        query = query.filter(Tag.type == type)
    
    tags = query.order_by(Tag.name).all()
    return tags

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    # Check for duplicate name
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名称已存在"
        )
    
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取单个标签"""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.is_deleted == False
    ).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    return tag

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db)
):
    """更新标签"""
    db_tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.is_deleted == False
    ).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    # Check for duplicate name if name is being changed
    if tag.name and tag.name != db_tag.name:
        existing = db.query(Tag).filter(Tag.name == tag.name, Tag.id != tag_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )

    update_data = tag.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tag, field, value)

    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """软删除标签"""
    db_tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.is_deleted == False
    ).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    db_tag.is_deleted = True
    db.commit()
    return None

@router.post("/{tag_id}/restore", response_model=TagResponse)
def restore_tag(tag_id: int, db: Session = Depends(get_db)):
    """恢复已删除的标签"""
    db_tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.is_deleted == True
    ).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在或未被删除"
        )

    db_tag.is_deleted = False
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/{tag_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """永久删除标签"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    db.delete(db_tag)
    db.commit()
    return None

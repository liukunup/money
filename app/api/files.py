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

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import hashlib
import os

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

router = APIRouter()


class ImportFromPathRequest(BaseModel):
    path: str
    source: Optional[str] = None  # 'alipay', 'wechatpay', 'auto'


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


@router.post("/from-path")
def import_from_path(
    request: ImportFromPathRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从本地路径导入支付宝/微信账单"""
    base_path = request.path
    source = request.source or 'auto'
    imported_files = []
    
    # 支持的数据目录
    data_dirs = []
    if os.path.exists(os.path.join(base_path, 'alipay')):
        data_dirs.append(('alipay', os.path.join(base_path, 'alipay')))
    if os.path.exists(os.path.join(base_path, 'wechatpay')):
        data_dirs.append(('wechatpay', os.path.join(base_path, 'wechatpay')))
    
    total_transactions = 0
    
    for platform, data_dir in data_dirs:
        if source != 'auto' and source != platform:
            continue
            
        # 遍历目录下的文件
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            if not os.path.isfile(file_path):
                continue
                
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.csv', '.xlsx', '.xls']:
                continue
                
            try:
                # 读取文件
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # 计算哈希
                file_hash = hashlib.sha256(content).hexdigest()
                
                # 检测文件类型
                parser = BillParser(db)
                file_type = parser._detect_csv_type(content)
                if file_type == 'unknown':
                    if ext in ['.xlsx', '.xls']:
                        file_type = 'excel'
                    else:
                        continue
                
                # 保存文件
                saved_path, _ = storage_service.save_file(current_user.id, content, filename)
                
                # 解析文件
                transactions = parser.parse(content, filename, file_type)
                
                # 创建导入记录
                import_record = ImportRecord(
                    file_name=filename,
                    file_type=file_type,
                    file_path=saved_path,
                    file_hash=file_hash,
                    status='parsed',
                    import_count=len(transactions),
                    user_id=current_user.id
                )
                db.add(import_record)
                db.commit()
                db.refresh(import_record)
                
                imported_files.append({
                    'file': filename,
                    'platform': platform,
                    'transactions': len(transactions),
                    'import_id': import_record.id
                })
                total_transactions += len(transactions)
                
            except Exception as e:
                imported_files.append({
                    'file': filename,
                    'error': str(e)
                })
    
    return {
        'success': True,
        'imported_files': imported_files,
        'total_transactions': total_transactions,
        'message': f'成功扫描 {len(imported_files)} 个文件，共 {total_transactions} 条交易记录'
    }

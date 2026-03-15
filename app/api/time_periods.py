from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.database import get_db
from app.models.time_period import TimePeriod
from app.schemas.time_period import TimePeriodCreate, TimePeriodUpdate, TimePeriodResponse

router = APIRouter()

@router.get("/", response_model=List[TimePeriodResponse])
def get_time_periods(
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取时间段列表"""
    query = db.query(TimePeriod)
    
    if type:
        query = query.filter(TimePeriod.type == type)
    
    time_periods = query.order_by(TimePeriod.start_date.desc()).all()
    return time_periods

@router.post("/", response_model=TimePeriodResponse, status_code=status.HTTP_201_CREATED)
def create_time_period(time_period: TimePeriodCreate, db: Session = Depends(get_db)):
    """创建时间段"""
    # Validate dates
    if time_period.end_date < time_period.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束日期必须大于或等于开始日期"
        )
    
    db_time_period = TimePeriod(**time_period.model_dump())
    db.add(db_time_period)
    db.commit()
    db.refresh(db_time_period)
    return db_time_period

@router.get("/{time_period_id}", response_model=TimePeriodResponse)
def get_time_period(time_period_id: int, db: Session = Depends(get_db)):
    """获取单个时间段"""
    time_period = db.query(TimePeriod).filter(TimePeriod.id == time_period_id).first()
    if not time_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间段不存在"
        )
    return time_period

@router.put("/{time_period_id}", response_model=TimePeriodResponse)
def update_time_period(
    time_period_id: int,
    time_period: TimePeriodUpdate,
    db: Session = Depends(get_db)
):
    """更新时间段落"""
    db_time_period = db.query(TimePeriod).filter(TimePeriod.id == time_period_id).first()
    if not db_time_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间段不存在"
        )

    update_data = time_period.model_dump(exclude_unset=True)
    
    # Validate dates if both are provided
    if 'start_date' in update_data and 'end_date' in update_data:
        if update_data['end_date'] < update_data['start_date']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期必须大于或等于开始日期"
            )
    elif 'start_date' in update_data:
        if db_time_period.end_date < update_data['start_date']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期必须大于或等于开始日期"
            )
    elif 'end_date' in update_data:
        if update_data['end_date'] < db_time_period.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期必须大于或等于开始日期"
            )

    for field, value in update_data.items():
        setattr(db_time_period, field, value)

    db.commit()
    db.refresh(db_time_period)
    return db_time_period

@router.delete("/{time_period_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_period(time_period_id: int, db: Session = Depends(get_db)):
    """删除时间段"""
    db_time_period = db.query(TimePeriod).filter(TimePeriod.id == time_period_id).first()
    if not db_time_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间段不存在"
        )

    db.delete(db_time_period)
    db.commit()
    return None

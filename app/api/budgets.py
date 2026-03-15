from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.db.database import get_db
from app.models.budget import Budget, BudgetAlert, PeriodType, AlertStatus
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse, BudgetWithUsage,
    BudgetAlertCreate, BudgetAlertUpdate, BudgetAlertResponse,
    BudgetUsageResponse, OverallBudgetSummary
)

router = APIRouter()


def get_current_period_dates(period_type: str) -> tuple[date, date]:
    """根据周期类型获取当前周期的开始和结束日期"""
    today = date.today()
    
    if period_type == "weekly":
        # 周一为开始
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period_type == "monthly":
        start = today.replace(day=1)
        # 下个月的第一天减一天
        if start.month == 12:
            end = date(start.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(start.year, start.month + 1, 1) - timedelta(days=1)
    elif period_type == "yearly":
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
    else:
        start = today.replace(day=1)
        if start.month == 12:
            end = date(start.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(start.year, start.month + 1, 1) - timedelta(days=1)
    
    return start, end


def calculate_spent_for_budget(budget: Budget, db: Session) -> Decimal:
    """计算预算已花费金额"""
    start_date, end_date = get_current_period_dates(budget.period_type)
    
    # 使用预算的 start_date 或当前周期开始日期
    period_start = max(budget.start_date, start_date)
    period_end = min(budget.end_date, end_date) if budget.end_date else end_date
    
    query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.type == "expense",
        Transaction.is_deleted == False,
        Transaction.date >= period_start,
        Transaction.date <= period_end
    )
    
    if budget.category_id:
        query = query.filter(Transaction.category_id == budget.category_id)
    
    result = query.scalar()
    return Decimal(str(result)) if result else Decimal("0")


def check_and_create_alert(budget: Budget, spent: Decimal, percent_used: float, db: Session):
    """检查并创建告警"""
    if percent_used >= 80 and budget.is_active:
        # 检查是否已存在80%的告警
        existing_alert = db.query(BudgetAlert).filter(
            BudgetAlert.budget_id == budget.id,
            BudgetAlert.threshold_percent == 80,
            BudgetAlert.status == AlertStatus.TRIGGERED
        ).first()
        
        if not existing_alert:
            alert = BudgetAlert(
                budget_id=budget.id,
                threshold_percent=80,
                status=AlertStatus.TRIGGERED,
                triggered_at=datetime.utcnow()
            )
            db.add(alert)
    
    if percent_used >= 100 and budget.is_active:
        # 检查是否已存在100%的告警
        existing_alert = db.query(BudgetAlert).filter(
            BudgetAlert.budget_id == budget.id,
            BudgetAlert.threshold_percent == 100,
            BudgetAlert.status == AlertStatus.TRIGGERED
        ).first()
        
        if not existing_alert:
            alert = BudgetAlert(
                budget_id=budget.id,
                threshold_percent=100,
                status=AlertStatus.TRIGGERED,
                triggered_at=datetime.utcnow()
            )
            db.add(alert)


@router.get("/", response_model=List[BudgetWithUsage])
def get_budgets(
    period_type: Optional[str] = Query(None, pattern="^(weekly|monthly|yearly)$"),
    category_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """获取预算列表（支持筛选）"""
    query = db.query(Budget)
    
    if active_only:
        query = query.filter(Budget.is_active == 1)
    
    if period_type:
        query = query.filter(Budget.period_type == period_type)
    if category_id:
        query = query.filter(Budget.category_id == category_id)
    
    budgets = query.order_by(Budget.created_at.desc()).all()
    
    # 计算每个预算的使用情况
    result = []
    for budget in budgets:
        spent = calculate_spent_for_budget(budget, db)
        remaining = budget.amount - spent
        percent_used = float(spent / budget.amount * 100) if budget.amount > 0 else 0
        
        # 检查并创建告警
        check_and_create_alert(budget, spent, percent_used, db)
        
        budget_data = BudgetWithUsage(
            id=budget.id,
            name=budget.name,
            category_id=budget.category_id,
            amount=budget.amount,
            period_type=budget.period_type,
            start_date=budget.start_date,
            end_date=budget.end_date,
            is_active=budget.is_active,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            spent=spent,
            remaining=remaining,
            percent_used=round(percent_used, 1),
            category_name=budget.category.name if budget.category else "Overall",
            category_icon=budget.category.icon if budget.category else "💰"
        )
        result.append(budget_data)
    
    db.commit()
    return result


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    """创建预算"""
    # 验证category_id是否存在
    if budget.category_id:
        category = db.query(Category).filter(
            Category.id == budget.category_id,
            Category.is_deleted == False
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    db_budget = Budget(**budget.model_dump())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.get("/{budget_id}", response_model=BudgetWithUsage)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    """获取单个预算"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    spent = calculate_spent_for_budget(budget, db)
    remaining = budget.amount - spent
    percent_used = float(spent / budget.amount * 100) if budget.amount > 0 else 0
    
    return BudgetWithUsage(
        id=budget.id,
        name=budget.name,
        category_id=budget.category_id,
        amount=budget.amount,
        period_type=budget.period_type,
        start_date=budget.start_date,
        end_date=budget.end_date,
        is_active=budget.is_active,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
        spent=spent,
        remaining=remaining,
        percent_used=round(percent_used, 1),
        category_name=budget.category.name if budget.category else "Overall",
        category_icon=budget.category.icon if budget.category else "💰"
    )


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget: BudgetUpdate,
    db: Session = Depends(get_db)
):
    """更新预算"""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    update_data = budget.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """删除预算"""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    db.delete(db_budget)
    db.commit()
    return None


@router.get("/analytics/usage", response_model=List[BudgetUsageResponse])
def get_budget_usage(
    period_type: Optional[str] = Query(None, pattern="^(weekly|monthly|yearly)$"),
    db: Session = Depends(get_db)
):
    """获取预算使用情况分析"""
    query = db.query(Budget).filter(Budget.is_active == 1)
    
    if period_type:
        query = query.filter(Budget.period_type == period_type)
    
    budgets = query.all()
    result = []
    
    for budget in budgets:
        spent = calculate_spent_for_budget(budget, db)
        remaining = budget.amount - spent
        percent_used = float(spent / budget.amount * 100) if budget.amount > 0 else 0
        
        # 获取触发的告警
        alerts = db.query(BudgetAlert).filter(
            BudgetAlert.budget_id == budget.id,
            BudgetAlert.status == AlertStatus.TRIGGERED
        ).all()
        
        period_start, period_end = get_current_period_dates(budget.period_type)
        
        result.append(BudgetUsageResponse(
            budget_id=budget.id,
            budget_name=budget.name,
            period_type=budget.period_type,
            start_date=max(budget.start_date, period_start),
            end_date=min(budget.end_date, period_end) if budget.end_date else period_end,
            amount=budget.amount,
            spent=spent,
            remaining=remaining,
            percent_used=round(percent_used, 1),
            is_over_budget=percent_used >= 100,
            alerts_triggered=[AlertStatus.TRIGGERED for _ in alerts]
        ))
    
    return result


@router.get("/analytics/summary", response_model=OverallBudgetSummary)
def get_budget_summary(db: Session = Depends(get_db)):
    """获取预算汇总"""
    budgets = db.query(Budget).filter(Budget.is_active == 1).all()
    
    total_budget_amount = sum(b.amount for b in budgets)
    total_spent = Decimal("0")
    
    budget_usages = []
    for budget in budgets:
        spent = calculate_spent_for_budget(budget, db)
        total_spent += spent
        remaining = budget.amount - spent
        percent_used = float(spent / budget.amount * 100) if budget.amount > 0 else 0
        
        budget_usages.append(BudgetWithUsage(
            id=budget.id,
            name=budget.name,
            category_id=budget.category_id,
            amount=budget.amount,
            period_type=budget.period_type,
            start_date=budget.start_date,
            end_date=budget.end_date,
            is_active=budget.is_active,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            spent=spent,
            remaining=remaining,
            percent_used=round(percent_used, 1),
            category_name=budget.category.name if budget.category else "Overall",
            category_icon=budget.category.icon if budget.category else "💰"
        ))
    
    return OverallBudgetSummary(
        total_budgets=len(budgets),
        active_budgets=len([b for b in budgets if b.is_active == 1]),
        total_budget_amount=total_budget_amount,
        total_spent=total_spent,
        total_remaining=total_budget_amount - total_spent,
        budgets=budget_usages
    )


# Budget Alerts endpoints
@router.get("/alerts", response_model=List[BudgetAlertResponse])
def get_alerts(
    budget_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(pending|triggered|resolved)$"),
    db: Session = Depends(get_db)
):
    """获取告警列表"""
    query = db.query(BudgetAlert)
    
    if budget_id:
        query = query.filter(BudgetAlert.budget_id == budget_id)
    if status:
        query = query.filter(BudgetAlert.status == status)
    
    return query.order_by(BudgetAlert.triggered_at.desc()).all()


@router.post("/alerts", response_model=BudgetAlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert: BudgetAlertCreate, db: Session = Depends(get_db)):
    """创建告警"""
    # 验证budget是否存在
    budget = db.query(Budget).filter(Budget.id == alert.budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    db_alert = BudgetAlert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.put("/alerts/{alert_id}", response_model=BudgetAlertResponse)
def update_alert(
    alert_id: int,
    alert: BudgetAlertUpdate,
    db: Session = Depends(get_db)
):
    """更新告警"""
    db_alert = db.query(BudgetAlert).filter(BudgetAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="告警不存在"
        )
    
    update_data = alert.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    if update_data.get("status") == "resolved":
        db_alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_alert)
    return db_alert


# Cash Flow Analytics (for Sankey chart)
@router.get("/analytics/cash-flow")
def get_cash_flow(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """获取资金流向数据（用于Sankey图）"""
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # 获取所有收入交易
    income_transactions = db.query(Transaction).filter(
        Transaction.type == "income",
        Transaction.is_deleted == False,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # 获取所有支出交易
    expense_transactions = db.query(Transaction).filter(
        Transaction.type == "expense",
        Transaction.is_deleted == False,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # 按分类汇总支出
    from collections import defaultdict
    expense_by_category = defaultdict(Decimal)
    income_by_category = defaultdict(Decimal)
    
    for t in expense_transactions:
        category = db.query(Category).filter(Category.id == t.category_id).first()
        category_name = category.name if category else "Other"
        expense_by_category[category_name] += Decimal(str(t.amount))
    
    for t in income_transactions:
        category = db.query(Category).filter(Category.id == t.category_id).first()
        category_name = category.name if category else "Other"
        income_by_category[category_name] += Decimal(str(t.amount))
    
    # 构建Sankey数据
    nodes = []
    links = []
    
    # 添加收入来源节点
    total_income = sum(income_by_category.values())
    nodes.append({"name": "Total Income"})
    income_index = len(nodes) - 1
    
    for category, amount in income_by_category.items():
        nodes.append({"name": category})
    
    # 添加支出分类节点
    nodes.append({"name": "Total Expense"})
    expense_index = len(nodes) - 1
    
    for category, amount in expense_by_category.items():
        nodes.append({"name": category})
    
    # 添加从收入到支出的连接（简化版：总收入 -> 各个支出分类）
    # 实际应该更复杂：收入来源 -> 总收入 -> 支出分类
    
    return {
        "nodes": nodes,
        "links": []
    }


# Spending Heatmap Data (for Heatmap chart)
@router.get("/analytics/heatmap")
def get_spending_heatmap(
    period: str = Query("month", pattern="^(week|month|year)$"),
    db: Session = Depends(get_db)
):
    """获取消费热力图数据"""
    today = date.today()
    
    if period == "week":
        # 过去8周的数据，按星期几聚合
        start_date = today - timedelta(weeks=8)
        transactions = db.query(Transaction).filter(
            Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.date >= start_date,
            Transaction.date <= today
        ).all()
        
        # 按星期几和小时聚合（这里只做星期几）
        from collections import defaultdict
        heatmap_data = defaultdict(Decimal)
        
        for t in transactions:
            weekday = t.date.weekday()  # 0=Monday, 6=Sunday
            heatmap_data[weekday] += Decimal(str(t.amount))
        
        # 转换为ECharts热力图格式
        result = []
        for weekday in range(7):
            result.append([weekday, 0, float(heatmap_data.get(weekday, 0))])
        
        return {"data": result, "period": "week"}
    
    elif period == "month":
        # 过去12个月的数据，按月份和日期聚合
        start_date = today - timedelta(days=365)
        transactions = db.query(Transaction).filter(
            Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.date >= start_date,
            Transaction.date <= today
        ).all()
        
        from collections import defaultdict
        heatmap_data = defaultdict(Decimal)
        
        for t in transactions:
            month = t.date.month
            day = t.date.day
            heatmap_data[(month, day)] += Decimal(str(t.amount))
        
        result = []
        for month in range(1, 13):
            for day in range(1, 32):
                value = float(heatmap_data.get((month, day), 0))
                if month in [1, 3, 5, 7, 8, 10, 12] or (month in [4, 6, 9, 11] and day <= 30) or (month == 2 and day <= 28):
                    result.append([month - 1, day - 1, value])
        
        return {"data": result, "period": "month"}
    
    else:
        # 按年份
        start_date = date(today.year - 3, 1, 1)
        transactions = db.query(Transaction).filter(
            Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.date >= start_date,
            Transaction.date <= today
        ).all()
        
        from collections import defaultdict
        heatmap_data = defaultdict(Decimal)
        
        for t in transactions:
            year = t.date.year
            month = t.date.month
            heatmap_data[(year, month)] += Decimal(str(t.amount))
        
        result = []
        for year in range(today.year - 3, today.year + 1):
            for month in range(1, 13):
                if year < today.year or month <= today.month:
                    value = float(heatmap_data.get((year, month), 0))
                    result.append([year - (today.year - 3), month - 1, value])
        
        return {"data": result, "period": "year"}
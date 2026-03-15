import sys
sys.path.append('.')

from app.db.database import engine, Base
from app.models import user, category, transaction, budget, tag, time_period, ai_provider

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)

    from app.db.database import SessionLocal
    db = SessionLocal()

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

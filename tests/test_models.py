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

def test_create_category():
    from app.models.category import Category
    category = Category(
        name="餐饮",
        type="expense",
        icon="🍽️"
    )
    assert category.name == "餐饮"
    assert category.type == "expense"

def test_create_transaction():
    from app.models.transaction import Transaction
    from datetime import date
    transaction = Transaction(
        amount=45.50,
        type="expense",
        category_id=1,
        date=date(2026, 3, 14),
        note="麦当劳午餐"
    )
    assert transaction.amount == 45.50
    assert transaction.type == "expense"

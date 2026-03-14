import pytest
from app.schemas.user import UserCreate, UserResponse
from datetime import datetime

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
        "email": "test@example.com",
        "display_name": None,
        "is_active": True,
        "created_at": datetime.now()
    }
    schema = UserResponse(**user_dict)
    assert schema.id == 1

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_transaction():
    response = client.post(
        "/api/transactions/",
        json={
            "amount": 45.50,
            "type": "expense",
            "category_id": 1,
            "date": "2026-03-14",
            "note": "麦当劳午餐"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert float(data["amount"]) == 45.50

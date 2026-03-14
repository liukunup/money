import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_category():
    response = client.post(
        "/api/categories/",
        json={
            "name": "餐饮",
            "type": "expense",
            "icon": "🍽️"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "餐饮"

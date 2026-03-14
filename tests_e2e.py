#!/usr/bin/env python3
"""
端到端测试脚本
测试完整的API流程
"""
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_api_endpoints():
    """测试所有API端点"""
    results = []

    # 测试 1: 根路径
    print_section("Test 1: Root Endpoint")
    try:
        response = client.get("/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert data["message"] == "Money API"
        results.append(("Root Endpoint", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Root Endpoint", f"FAIL: {e}"))

    # 测试 2: 用户注册
    print_section("Test 2: User Registration")
    try:
        user_data = {
            "username": "testuser_e2e",
            "email": "test_e2e@example.com",
            "password": "testpass123"
        }
        response = client.post("/api/users/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Request: {json.dumps(user_data, indent=2)}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 201
        assert data["username"] == "testuser_e2e"
        assert data["email"] == "test_e2e@example.com"
        results.append(("User Registration", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("User Registration", f"FAIL: {e}"))

    # 测试 3: 用户登录
    print_section("Test 3: User Login")
    try:
        login_data = {
            "username": "testuser_e2e",
            "password": "testpass123"
        }
        response = client.post("/api/users/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Request: {json.dumps(login_data, indent=2)}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        results.append(("User Login", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("User Login", f"FAIL: {e}"))

    # 测试 4: 创建分类
    print_section("Test 4: Create Category")
    try:
        category_data = {
            "name": "测试分类",
            "type": "expense",
            "icon": "🧪"
        }
        response = client.post("/api/categories/", json=category_data)
        print(f"Status: {response.status_code}")
        print(f"Request: {json.dumps(category_data, indent=2)}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 201
        assert data["name"] == "测试分类"
        assert data["type"] == "expense"
        results.append(("Create Category", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Create Category", f"FAIL: {e}"))

    # 测试 5: 获取分类列表
    print_section("Test 5: Get Categories List")
    try:
        response = client.get("/api/categories/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response count: {len(data)}")
        print(f"Categories: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) >= 9  # 至少有9个预设分类
        results.append(("Get Categories List", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Get Categories List", f"FAIL: {e}"))

    # 测试 6: 按类型筛选分类
    print_section("Test 6: Get Categories by Type")
    try:
        response = client.get("/api/categories/?type=expense")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response count: {len(data)}")
        print(f"Expense categories: {json.dumps([c['name'] for c in data], indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert all(cat["type"] == "expense" for cat in data)
        results.append(("Get Categories by Type", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Get Categories by Type", f"FAIL: {e}"))

    # 测试 7: 创建交易
    print_section("Test 7: Create Transaction")
    try:
        # 先获取一个分类ID
        categories_resp = client.get("/api/categories/?type=expense")
        categories = categories_resp.json()
        category_id = categories[0]["id"]
        
        transaction_data = {
            "amount": 100.50,
            "type": "expense",
            "category_id": category_id,
            "date": "2026-03-14",
            "note": "端到端测试交易"
        }
        response = client.post("/api/transactions/", json=transaction_data)
        print(f"Status: {response.status_code}")
        print(f"Request: {json.dumps(transaction_data, indent=2)}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 201
        assert float(data["amount"]) == 100.50
        results.append(("Create Transaction", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Create Transaction", f"FAIL: {e}"))

    # 测试 8: 获取交易列表
    print_section("Test 8: Get Transactions List")
    try:
        response = client.get("/api/transactions/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response count: {len(data)}")
        print(f"Transactions: {json.dumps(data, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert isinstance(data, list)
        results.append(("Get Transactions List", "PASS"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Get Transactions List", f"FAIL: {e}"))

    # 测试 9: 获取单个交易
    print_section("Test 9: Get Single Transaction")
    try:
        transactions_resp = client.get("/api/transactions/")
        transactions = transactions_resp.json()
        if transactions:
            transaction_id = transactions[0]["id"]
            response = client.get(f"/api/transactions/{transaction_id}")
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            assert response.status_code == 200
            assert data["id"] == transaction_id
            results.append(("Get Single Transaction", "PASS"))
        else:
            print("No transactions to test")
            results.append(("Get Single Transaction", "SKIP"))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append(("Get Single Transaction", f"FAIL: {e}"))

    # 打印测试报告
    print_section("Test Summary")
    passed = sum(1 for _, status in results if status == "PASS")
    failed = sum(1 for _, status in results if "FAIL" in status)
    skipped = sum(1 for _, status in results if "SKIP" in status)
    
    for test_name, status in results:
        status_icon = "✓" if status == "PASS" else ("✗" if "FAIL" in status else "○")
        print(f"{status_icon} {test_name}: {status}")
    
    print(f"\n{'='*60}")
    print(f"  Total: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Success Rate: {(passed/len(results)*100):.1f}%")
    print(f"{'='*60}")

    # 保存测试报告到文件
    report = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "success_rate": round(passed/len(results)*100, 1),
        "tests": [{"name": name, "status": status} for name, status in results]
    }
    
    with open("/tmp/e2e-test-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n测试报告已保存到: /tmp/e2e-test-report.json")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = test_api_endpoints()
    sys.exit(0 if success else 1)

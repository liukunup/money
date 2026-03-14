# Money - 极简AI驱动个人记账工具

Money 是一款轻量级的智能个人记账工具，帮助你轻松管理收支记录和分类。

## 功能特性

- ✅ **用户认证**: 注册、登录
- ✅ **分类管理**: 创建、查询、删除收支分类
- ✅ **交易记录**: 记录和管理每笔收支
- ✅ **筛选查询**: 按类型、日期范围、分类筛选交易
- 🔜 **AI 功能**: 智能分类和支出分析（开发中）

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **验证**: Pydantic v2
- **认证**: JWT (python-jose + passlib)
- **数据库**: SQLite
- **测试**: pytest

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **测试**: Vitest
- **UI 组件**: Apple Design 风格（开发中）

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+
- uv (Python 包管理器)

### 安装依赖

```bash
# 安装后端依赖
cd /path/to/money
uv sync

# 安装前端依赖（如果需要）
cd webui
npm install
```

### 初始化数据库

```bash
python -m scripts.init_db
```

### 启动后端服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 将在 `http://localhost:8000` 运行

### 启动前端开发服务器

```bash
cd webui
npm run dev
```

前端开发服务器将在 `http://localhost:5173` 运行

## API 文档

### 认证接口

#### 用户注册
```
POST /api/users/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}

响应: 201 Created
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "display_name": "testuser",
  "is_active": true,
  "created_at": "2026-03-14T12:00:00.000000Z"
}
```

#### 用户登录
```
POST /api/users/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}

响应: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 分类接口

#### 创建分类
```
POST /api/categories/
Content-Type: application/json

{
  "name": "餐饮",
  "type": "expense",
  "icon": "🍽️"
}

响应: 201 Created
{
  "id": 1,
  "name": "餐饮",
  "type": "",
  "icon": "🍽️",
  "created_at": "2026-03-14T12:00:00.000000Z"
}
```

#### 获取分类列表
```
GET /api/categories/?type=expense
GET /api/categories/

响应: 200 OK
[
  {
    "id": 1,
    "name": "餐饮",
    "type": "expense",
    "icon": "🍽️",
    "created_at": "2026-03-14T12:00:00.000000Z"
  }
]
```

#### 获取单个分类
```
GET /api/categories/{category_id}

响应: 200 OK
{
  "id": 1,
  "name": "餐饮",
  "type": "expense",
  "icon": "创建的分类",
  "created_at": "2026-03-14T12:00:00.000000Z"
}
```

#### 删除分类
```
DELETE /api/categories/{category_id}

响应: 204 No Content
```

### 交易接口

#### 创建交易
```
POST /api/transactions/
Content-Type: application/json

{
  "amount": 100.50,
  "type": "expense",
  "category_id": 1,
  "date": "2026-03-14",
  "note": "麦当劳午餐"
}

响应: 201 Created
{
  "id": 1,
  "amount": "100.50",
  "type": "expense",
  "category_id": 1,
  "date": "2026-03-14",
  "note": "麦当劳午餐",
  "created_at": "2026-03-14T12:00:00.000000Z"
}
```

#### 获取交易列表
```
GET /api/transactions/
GET /api/transactions/?type=expense&category_id=1&start_date=2026-01-01&end_date=2026-12-31
GET /api/transactions/

响应: 200 OK
[
  {
    "id": 1,
    "amount": "100.50",
    "type": "expense",
    "category_id": 1,
    "date": "2026-03-14",
    "note": "测试交易",
    "created_at": "2026-03-14T12:00:00.000000Z"
  }
]
```

#### 获取单个交易
```
GET /api/transactions/{transaction_id}

响应: 200 OK
{
  "id": 1,
  "amount": "100.50",
  "type": "expense",
  "category_id": 1,
  "date": "2026-03-14",
  "note": "麦当劳午餐",
  "created_at": "2026-0-3-14T12:00:00.000000Z"
}
```

#### 更新交易
```
PUT /api/transactions/{transaction_id}
Content-Type: application/json

{
  "amount": 150.00,
  "note": "更新后的备注"
}

响应: 200 OK
{
  "id": 1,
  "amount": "150.00",
  "type": "expense",
  "category_id": 1,
  "date": "2026-03-14",
  "note": "更新后的备注",
  "created_at": "2026-03-14T12:00:00.000000Z"
}
```

#### 删除交易
```
DELETE /api/transactions/{transaction_id}

响应: 204 No Content
```

## 环境变量

创建 `.env` 文件来配置应用（参考 `.env.example`）：

```bash
cp .env.example .env
```

主要环境变量：
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT 密钥（生产环境必须更改）
- `DEBUG`: 调试模式开关
- `BACKEND_CORS_ORIGINS`: CORS 允许的源列表

## 数据库

默认数据库路径: `./data/money.db`

预设分类:
- 支出分类：餐饮、交通、购物、娱乐、住房、医疗、教育、其他
- 收入分类：工资、奖金、投资、兼职、其他收入

## 开发

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_models.py -v

# 运行端到端测试
python tests_e2e.py
```

### 运行数据库迁移（如果需要）

```bash
python -m scripts.init_db
```

## 部署

### Docker 部署（推荐）

```bash
# 构建并启动
docker build -t money
docker run -p 8000:80 money
```

应用将在 `http://localhost:8000` 访问

### 手动部署

```bash
# 确保依赖已安装
uv sync

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
money/
├── app/                 # 后端应用
│   ├── api/          # API 路由
│   ├── core/          # 核心配置
│   ├── db/            # 数据库
│   ├── models/         # 数据模型
│   ├── schemas/       # Pydantic 模式
│   └── main.py        # 应用入口
├── tests/              # 测试
│   ├── api/            # API 测试
│   ├── models/         # 模型测试
│   └── test_*.py      # 其他测试
├── scripts/             # 实用脚本
│   └── init_db.py    # 数据库初始化
├── data/                # 数据目录（SQLite 数据库）
├── pyproject.toml       # 项目配置
├── Dockerfile           # Docker 配置
└── webui/              # 前端应用
```

## 测试覆盖率

- 单元测试：配置、模型、Schema
- API测试：用户、分类、交易
- 端到端测试：完整的API流程

当前测试通过率：**100%** (9/9)

## 贡献

欢迎贡献！请阅读以下指南：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或 Pull Request。

## 路线图

- [x] 项目结构初始化
- [x] 核心配置
- [x] 数据库模型
- [x] Pydantic Schemas
- [x] 用户认证 API
- [x] 分类管理 API
- [x] 交易记录 API
- [x] 数据库初始化
- [x] Docker 配置
- [x] 测试覆盖
- [ ] 前端 Vue 3 应用
- [ ] Apple Design UI 组件
- [ ] 数据可视化
- [ ] 软删除功能
- [ ] 多用户支持
- [ ] AI 功能集成

## 更新日志

### v0.1.0 (2026-03-14)
- ✅ 完成后端 MVP 实现
- ✅ 实现用户认证、分类管理、交易记录 API
- ✅ 端到端测试通过率 100%
- 📝 编写完整的 README 文档

---

**Money** - 让记账变得简单智能！

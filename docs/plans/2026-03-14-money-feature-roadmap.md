# Money - 极简AI驱动个人记账工具

## 设计文档

**创建日期**: 2026-03-14
**最后更新**: 2026-03-14
**版本**: v1.3
**作者**: Sisyphus

## 变更日志

**v1.3 (2026-03-14)**
- 新增家庭多用户支持（夫妻/家庭成员）
- 新增家庭数据合并展示和分析
- 新增家庭成员权限管理

**v1.2 (2026-03-14)**
- 新增 AI 服务管理功能（支持多模型、OpenAI 兼容接口）
- 新增桑基图展示资金流向
- 新增看板截图分享功能

**v1.1 (2026-03-14)**
- 新增支付宝/微信支付数据导入功能（CSV/Excel）
- 新增截图自动解析功能（OCR 识别）
- 新增移动端适配（响应式设计 + PWA）
- 更新优先级排序，导入和移动端提升至 P0
- 添加相关数据库表和 API 设计

**v1.0 (2026-03-14)**
- 初始版本
- 定义基础架构和功能路线图

---

## 1. 项目概述

### 1.1 核心定位

Money 是一款极简的 AI 驱动个人记账工具，针对理财新手设计，通过强大的 AI 能力和数据驱动功能，帮助用户建立良好的财务习惯。

### 1.2 目标用户

- 理财新手
- 需要智能辅助的精打细算者
- 追求数据驱动的用户
- 偏好极简设计的用户

### 1.3 核心价值主张

- **极致简洁**：零学习成本，3秒完成记账
- **AI 智能化**：自动分类、智能建议、异常检测
- **数据驱动**：丰富的可视化洞察，掌控财务状况
- **隐私安全**：本地数据存储，可选云同步
- **一键部署**：Docker 单一镜像，开箱即用

---

## 2. 技术架构

### 2.1 整体架构

采用前后端分离架构，Docker 单一镜像部署：

```
┌─────────────────────────────────────┐
│         Docker 容器                  │
│  ┌────────────┐    ┌─────────────┐  │
│  │   Nginx   │───▶│  FastAPI    │  │
│  │ (静态文件) │    │  (后端API)  │  │
│  └────────────┘    └──────┬──────┘  │
│                           │         │
│                      ┌────▼────┐    │
│                      │ SQLite  │    │
│                      │ (数据库) │    │
│                      └─────────┘    │
└─────────────────────────────────────┘
```

### 2.2 技术栈

#### 前端
- **框架**: Vue 3.5 + TypeScript
- **构建**: Vite 6
- **路由**: Vue Router 4
- **状态管理**: Pinia 3
- **图表库**: ECharts
- **UI 组件**: 自定义组件库（保持极简）
- **移动端适配**: 响应式设计 + PWA 支持
- **文件上传**: 文件导入/截图上传组件

#### 后端
- **框架**: FastAPI (Python 3.12+)
- **数据库**: SQLite
- **AI 服务**: OpenAI API / 本地 LLM
- **数据分析**: Pandas, Scikit-learn
- **用户认证**: JWT + PBKDF2（密码加密）
- **权限管理**: 基于角色的访问控制（RBAC）

#### 部署
- **容器**: Docker
- **反向代理**: Nginx
- **数据持久化**: Volume 挂载

### 2.3 数据流

```
用户操作 → 前端界面 → REST API → FastAPI → SQLite
                                       ↓
用户 ← 响应数据 ← 前端渲染 ← JSON 响应 ← AI引擎（可选）
```

---

## 3. 功能路线图

### 阶段1：基础记账系统（MVP）

#### 3.1 核心功能
- 收支记录（金额、日期、分类、备注）
- 分类管理（预设分类 + 自定义分类）
- 基础查询（按日期、分类、金额筛选）
- 数据持久化（SQLite 本地存储）

#### 3.2 前端组件
- **记账表单**: 快速添加收支
- **交易列表**: 历史记录展示
- **分类管理**: 分类增删改
- **截图上传**: 支付截图识别组件
- **文件导入**: CSV/Excel 导入组件
- **移动端适配**: 响应式布局、FAB 快速记账按钮、底部导航栏

#### 3.3 后端 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/transactions | 创建交易 |
| GET | /api/transactions | 获取交易列表（支持筛选） |
| PUT | /api/transactions/:id | 更新交易 |
| DELETE | /api/transactions/:id | 删除交易 |
| GET | /api/categories | 获取分类列表 |
| POST | /api/categories | 创建分类 |

#### 3.3.1 支付宝/微信支付数据导入

**功能特性**：
- 支持支付宝/微信账单 CSV/Excel 文件导入
- 自动解析支付平台账单格式
- 智能匹配分类和金额
- 批量导入进度显示
- 导入数据校验（去重、异常值检测）

**技术实现**：
- 后端使用 `pandas` 解析 CSV/Excel
- 支付宝账单格式识别（标准 CSV 格式）
- 微信账单格式识别（标准 CSV 格式）
- 数据清洗和标准化
- AI 辅助分类（基于备注和商户名称）

**后端 API**：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/import/parse | 解析上传的账单文件 |
| POST | /api/import/preview | 预览导入数据（未保存） |
| POST | /api/import/confirm | 确认导入数据到数据库 |
| GET | /api/import/history | 导入历史记录 |

#### 3.3.2 截图自动解析

**功能特性**：
- 支持上传支付宝/微信支付截图
- AI OCR 识别截图中的交易信息
- 自动提取：金额、日期、商户、备注
- 智能分类匹配
- 支持批量截图上传

**技术实现**：
- 前端使用 Tesseract.js 或调用后端 OCR API
- 后端集成 PaddleOCR 或 Tesseract OCR
- 使用 LLM 提取结构化数据（OpenAI Vision API）
- 数据校验和清洗

**后端 API**：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/ocr/upload | 上传截图并解析 |
| POST | /api/ocr/ai-extract | AI 提取交易数据 |
| GET | /api/ocr/history | OCR 历史记录 |

#### 3.3.3 新增依赖

```python
# pyproject.toml
dependencies = [
    "fastapi[standard]>=0.115.12",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",           # Excel 支持
    "paddleocr>=2.7.0",           # OCR 引擎
    "pillow>=10.0.0",             # 图像处理
    "python-jose[cryptography]>=3.3.0",  # JWT Token
    "passlib[bcrypt]>=1.7.4",     # 密码加密
    "python-multipart>=0.0.9",    # 文件上传支持
]
```

#### 3.3.4 移动端适配 API

**移动端专用 API**：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/transactions/quick | 快速记账（简化参数） |
| GET | /api/analytics/quick | 快速统计（仅核心数据） |

#### 3.4 数据库 Schema

```sql
CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(50) NOT NULL,
  type VARCHAR(10) NOT NULL,  -- 'income' or 'expense'
  icon VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  amount DECIMAL(10, 2) NOT NULL,
  type VARCHAR(10) NOT NULL,  -- 'income' or 'expense'
  category_id INTEGER NOT NULL,
  date DATE NOT NULL,
  note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 导入记录表
CREATE TABLE import_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(20) NOT NULL,  -- 'alipay', 'wechat', 'excel', 'csv'
  import_count INTEGER NOT NULL,   -- 导入的交易数量
  skip_count INTEGER DEFAULT 0,     -- 跳过的数量（重复或无效）
  status VARCHAR(20) NOT NULL,     -- 'pending', 'completed', 'failed'
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OCR 识别记录表
CREATE TABLE ocr_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  image_path VARCHAR(255) NOT NULL,
  extracted_data TEXT,             -- JSON 格式的提取数据
  is_confirmed BOOLEAN DEFAULT FALSE,
  transaction_id INTEGER,           -- 关联的交易ID
  confidence_score DECIMAL(3, 2),  -- 识别置信度 0.00-1.00
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);
```

---

### 阶段2：数据可视化

#### 3.5 核心功能
- 仪表盘首页（收支总览、本月统计）
- 趋势图表（收支曲线、月度对比）
- 分类饼图（消费类别占比）
- 交易热力图（按星期/时间段消费习惯）
- 桑基图（资金流向可视化：收入→分类→支出）
- 看板截图分享（导出仪表盘为图片）

#### 3.6 前端组件
- **Dashboard.vue**: 仪表盘主页
- **TrendChart.vue**: 趋势图组件
- **PieChart.vue**: 饼图组件
- **Heatmap.vue**: 热力图组件
- **SankeyChart.vue**: 桑基图组件
- **DashboardShare.vue**: 看板截图分享组件
- **TimeRangeSelector.vue**: 时间范围选择器

#### 3.7 后端 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/analytics/summary | 总览数据（总收支、余额） |
| GET | /api/analytics/trends | 趋势数据（按时间段分组） |
| GET | /api/analytics/by-category | 分类统计 |
| GET | /api/analytics/heatmap | 热力图数据 |
| GET | /api/analytics/sankey | 桑基图数据（资金流向） |
| POST | /api/analytics/screenshot | 生成看板截图（后端渲染） |
| GET | /api/analytics/screenshot/:id | 获取生成的截图 |

#### 3.8 性能优化

```sql
-- 添加索引提升查询性能
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);
```

#### 3.8.1 桑基图数据结构

**桑基图节点定义**：
- **收入来源节点**：工资、投资、兼职等收入类别
- **中间分类节点**：日常消费、储蓄、投资、偿还等大分类
- **支出目标节点**：餐饮、交通、购物等具体消费类别

**数据流向**：
```
收入来源 → 资金分配 → 具体支出
工资(10000) → 储蓄(3000) → 银行存款
           → 日常消费(5000) → 餐饮(1500)
                         → 交通(500)
                         → 购物(3000)
           → 投资(2000) → 基金(2000)
```

**后端数据格式**（ECharts Sankey 格式）：
```json
{
  "nodes": [
    {"name": "工资", "category": "收入"},
    {"name": "日常消费", "category": "分配"},
    {"name": "餐饮", "category": "支出"}
  ],
  "links": [
    {"source": "工资", "target": "日常消费", "value": 5000},
    {"source": "日常消费", "target": "餐饮", "value": 1500}
  ]
}
```

#### 3.8.2 看板截图分享

**技术方案**：

**方案 A（推荐）：后端渲染**
- 使用 Playwright 或 Puppeteer 后端渲染仪表盘
- 生成高质量 PNG 图片
- 支持自定义尺寸和日期范围

**方案 B：前端 Canvas 导出**
- 使用 html2canvas 前端导出
- 无需后端支持
- 但可能受浏览器安全限制

**实现细节（方案 A）**：

后端依赖：
```python
# pyproject.toml
dependencies = [
    "playwright>=1.40.0",
    "playwright-stealth>=1.0.6",  # 避免被检测
]
```

截图生成流程：
1. 接收截图请求（包含时间范围、图表配置）
2. 后端启动无头浏览器
3. 加载仪表盘页面并注入数据
4. 等待图表渲染完成
5. 生成截图并保存到文件系统或返回 base64
6. 定期清理过期截图（24小时后删除）

截图配置：
```json
{
  "width": 1200,
  "height": 800,
  "full_page": false,
  "include_charts": ["trend", "pie", "sankey"],
  "date_range": "2026-03-01 to 2026-03-31"
}
```

---

### 阶段3：预算模块

#### 3.9 核心功能
- 预算设定（按分类、按时间周期）
- 实时预算进度（已用/预算总额）
- 超支预警（达到 80%、100% 阈值提醒）
- 预算历史记录（每月预算对比）

#### 3.10 前端组件
- **BudgetList.vue**: 预算列表
- **BudgetProgress.vue**: 预算进度条
- **BudgetForm.vue**: 预算设置表单
- **BudgetComparison.vue**: 预算对比视图

#### 3.11 后端 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/budgets | 获取预算列表 |
| POST | /api/budgets | 创建预算 |
| PUT | /api/budgets/:id | 更新预算 |
| DELETE | /api/budgets/:id | 删除预算 |
| GET | /api/budgets/usage | 获取预算使用情况 |

#### 3.12 数据库 Schema

```sql
CREATE TABLE budgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  period_type VARCHAR(20) NOT NULL,  -- 'monthly', 'weekly', 'yearly'
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE budget_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  budget_id INTEGER NOT NULL,
  threshold_percent INTEGER NOT NULL,  -- 80, 100
  triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20) DEFAULT 'unread',  -- 'unread', 'read', 'dismissed'
  FOREIGN KEY (budget_id) REFERENCES budgets(id)
);
```

---

### 阶段4：AI 能力集成

#### 3.13 核心功能
- 智能分类（自动识别交易类别）
- 消费建议（基于历史数据）
- 异常检测（识别异常大额支出）
- 消费预测（未来支出趋势）

#### 3.14 AI 集成方案

**方案 A（推荐）**: OpenAI API
- 优势：智能程度高，无需训练，快速上线
- 成本：按使用量计费，可控
- 适用：初期 MVP，快速验证需求

**方案 B**: 本地轻量级模型
- 优势：隐私好，零 API 成本
- 缺点：需要训练，性能要求高
- 适用：后期优化，隐私敏感用户

**方案 C**: 启发式规则算法
- 优势：零成本，响应快
- 缺点：智能程度有限
- 适用：作为 AI 的降级方案

#### 3.15 前端组件
- **AISuggestionCard.vue**: AI 建议卡片
- **AnomalyMarker.vue**: 异常交易标记
- **SmartClassificationToggle.vue**: 智能分类开关

#### 3.16 后端 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/ai/classify | 智能分类交易 |
| GET | /api/ai/suggestions | 获取消费建议 |
| GET | /api/ai/anomalies | 获取异常交易 |
| GET | /api/ai/predict | 支出预测 |

#### 3.16.1 AI 服务管理功能

**功能特性**：
- 支持录入多个 AI 服务提供商（OpenAI、Azure OpenAI、本地 LLM 等）
- 每个服务可配置多个模型（gpt-4o, gpt-3.5-turbo, claude-3 等）
- 支持 OpenAI 兼容接口（统一的 API 调用格式）
- 管理员可切换默认使用的模型
- 支持模型优先级和降级策略（主模型失败时自动切换）

**技术实现**：
- 后端存储 AI 服务配置（API Key、Base URL、模型列表）
- 统一的 AI 服务调用接口（适配不同提供商）
- 支持自定义提示词模板（针对不同任务的 Prompt）

**后端 API（管理端）**：

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/admin/ai-providers | 获取 AI 服务列表 |
| POST | /api/admin/ai-providers | 创建 AI 服务配置 |
| PUT | /api/admin/ai-providers/:id | 更新 AI 服务配置 |
| DELETE | /api/admin/ai-providers/:id | 删除 AI 服务配置 |
| POST | /api/admin/ai-providers/:id/test | 测试 AI 服务连接 |
| GET | /api/admin/ai-models | 获取所有可用模型列表 |
| PUT | /api/admin/ai-models/default | 设置默认模型 |

**AI 服务配置示例**：

```json
{
  "name": "OpenAI",
  "provider_type": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-xxxxx",
  "models": [
    {
      "name": "gpt-4o",
      "max_tokens": 128000,
      "use_for": ["classify", "suggest", "predict"]
    },
    {
      "name": "gpt-4o-mini",
      "max_tokens": 128000,
      "use_for": ["classify", "suggest"]
    },
    {
      "name": "gpt-3.5-turbo",
      "max_tokens": 16385,
      "use_for": ["classify"]
    }
  ],
  "is_active": true,
  "priority": 1
}
```

**支持的提供商类型**：
- `openai`: OpenAI 官方 API
- `azure_openai`: Azure OpenAI Service
- `anthropic`: Claude (Anthropic)
- `local`: 本地 LLM（兼容 OpenAI API 格式）
- `custom`: 自定义兼容接口

**降级策略**：
1. 优先使用优先级最高的活跃服务
2. 如果失败（超时、限流、错误），自动切换到下一个
3. 记录切换日志用于监控
4. 支持手动禁用某个服务

#### 3.17 AI 实现策略

**初期**：
- 基于规则的关键词匹配（简单快速）
- 预设 20+ 常见分类规则

**中期**：
- OpenAI GPT-4o mini（智能分类、建议）
- 上下文：用户历史交易数据

**长期**：
- 基于用户数据微调本地模型
- 隐私 + 个性化

---

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────┐       ┌──────────────┐       ┌────────────┐
│ categories  │ 1   * │ transactions │ *   1 │  budgets   │
├─────────────┤       ├──────────────┤       ├────────────┤
│ id (PK)     │◀──────│ id (PK)      │──────▶│ id (PK)    │
│ name        │       │ amount       │       │ amount     │
│ type        │       │ type         │       │ period_type│
│ icon        │       │ category_id  │       │ start_date │
│ created_at  │       │ date         │       │ end_date   │
└─────────────┘       │ note         │       └────────────┘
                       │ created_at   │              │
                       │ user_id     │              │
                       └──────────────┘              │
                          ▲                         │
                          │ 1                       │
                          │                         │ *   * │
                          │                         ▼       │
┌──────────────┐       1 │                  ┌─────────────┐
│  households  │─────────┤                  │budget_alerts│
├──────────────┤ 1   * │                  ├─────────────┤
│ id (PK)      │◀──────┤                  │ id (PK)     │
│ name         │       │                  │ budget_id   │
│ created_at   │ 1   *│                  │ threshold   │
└──────────────┤       │                  │ triggered_at│
                 │    └──────────────┐   │ status      │
                 ▼                   │   └─────────────┘
         ┌──────────────┐ 1   *     │
         │  members     │◀───────────┘
         ├──────────────┤       │     ┌──────────────┐ 1   * ┌──────────────┐
         │ id (PK)      │  *    1│    │ai_providers  │◀──────│ ai_models     │
         │ household_id │◀───────┘    ├──────────────┤       ├──────────────┤
         │ user_id      │             │ id (PK)      │       │ id (PK)      │
         │ role         │             │ name         │       │ provider_id   │
         │ permissions  │             │ provider_type│       │ model_name    │
         │ created_at   │             │ base_url     │       │ max_tokens   │
         └──────────────┘             │ api_key      │       │ use_for      │
                                     │ is_active    │       │ is_default   │
                                     │ priority     │       └──────────────┘
                                     └──────────────┘
```
└──────────────┘
```

### 4.2 索引设计

```sql
-- 交易表索引
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_date_type ON transactions(date, type);

-- 预算表索引
CREATE INDEX idx_budgets_period ON budgets(start_date, end_date);
CREATE INDEX idx_budgets_category ON budgets(category_id);

-- 预算告警索引
CREATE INDEX idx_budget_alerts_budget ON budget_alerts(budget_id);
CREATE INDEX idx_budget_alerts_status ON budget_alerts(status);

-- 家庭相关索引
CREATE INDEX idx_households_created_at ON households(created_at);
CREATE INDEX idx_members_household ON members(household_id);
CREATE INDEX idx_members_user ON members(user_id);
```

### 4.3 家庭多用户数据库 Schema

```sql
-- 用户表（替代原来的单用户设计）
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(50),
  avatar_url VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 家庭表
CREATE TABLE households (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  currency VARCHAR(10) DEFAULT 'CNY',
  timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 家庭成员表（关联用户和家庭）
CREATE TABLE members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  household_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  role VARCHAR(20) NOT NULL,  -- 'owner', 'admin', 'member'
  permissions TEXT,             -- JSON 格式的权限配置
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(household_id, user_id)
);

-- 更新交易表，添加 user_id 和 household_id
ALTER TABLE transactions ADD COLUMN user_id INTEGER;
ALTER TABLE transactions ADD COLUMN household_id INTEGER;
ALTER TABLE transactions ADD FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE transactions ADD FOREIGN KEY (household_id) REFERENCES households(id);
ALTER TABLE transactions ADD INDEX idx_transactions_user ON transactions(user_id);
ALTER TABLE transactions ADD INDEX idx_transactions_household ON transactions(household_id);

-- 更新预算表，支持家庭预算
ALTER TABLE budgets ADD COLUMN household_id INTEGER;
ALTER TABLE budgets ADD FOREIGN KEY (household_id) REFERENCES households(id);
ALTER TABLE budgets ADD INDEX idx_budgets_household ON budgets(household_id);
```

### 4.4 家庭场景功能设计

#### 4.4.1 家庭成员管理

**核心功能**：
- 创建家庭（邀请配偶/家人）
- 邀请成员加入家庭（通过邀请码或链接）
- 设置成员角色和权限
- 成员列表管理

**角色权限设计**：

| 角色 | 权限 |
|------|------|
| **Owner** | 家庭完整控制权、成员管理、预算设置、删除家庭 |
| **Admin** | 交易管理、预算管理、成员查看（不可删除家庭） |
| **Member** | 只能记账、查看数据、查看预算（不可修改设置） |

**权限配置示例**：
```json
{
  "can_create_transactions": true,
  "can_edit_own_transactions": true,
  "can_edit_all_transactions": false,
  "can_delete_transactions": false,
  "can_view_all_transactions": true,
  "can_create_budgets": false,
  "can_edit_budgets": false,
  "can_invite_members": false,
  "can_manage_ai_providers": false
}
```

#### 4.4.2 家庭数据合并展示

**核心功能**：
- 家庭总览（合并所有成员的收支）
- 成员对比（横向对比各成员消费情况）
- 分类汇总（按分类合并家庭总消费）
- 时间范围筛选（查看特定时间段的合并数据）

**数据合并策略**：
```sql
-- 家庭总收支统计
SELECT
  user_id,
  SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
  SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
FROM transactions
WHERE household_id = ?
GROUP BY user_id;

-- 家庭分类汇总
SELECT
  c.name as category_name,
  c.type as category_type,
  SUM(t.amount) as total_amount,
  COUNT(*) as transaction_count
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.household_id = ?
GROUP BY c.id
ORDER BY total_amount DESC;
```

**前端可视化**：
- **家庭仪表盘**：展示家庭总收支、各成员占比
- **成员对比图**：堆叠柱状图对比各成员消费
- **分类合并图**：展示家庭总消费分类占比
- **成员贡献图**：展示各成员对家庭收入的贡献

#### 4.4.3 家庭预算

**核心功能**：
- 设定家庭预算（按分类或总预算）
- 预算进度追踪（实时显示已用/总额）
- 超支预警（通知所有家庭成员）
- 成员预算分配（可选：为每个成员分配子预算）

**预算类型**：
- **家庭共享预算**：所有成员共同使用的预算
- **分类预算**：特定分类的消费限制
- **成员预算**：为单个成员设定的预算

**预警策略**：
- 达到 80%：通知所有成员
- 达到 100%：紧急提醒
- 超过 100%：标记超支，记录日志

#### 4.4.4 家庭数据隐私

**核心功能**：
- 成员隐私保护（可选隐藏个人具体消费）
- 数据可见性控制（谁可以看到谁的数据）
- 导出时选择导出范围（个人/家庭）

**可见性级别**：
- **完全公开**：所有成员可以查看彼此所有交易
- **分类公开**：只显示分类，不显示具体金额和备注
- **仅汇总**：只显示汇总统计，不显示明细
- **完全隐私**：个人数据仅自己可见

**后端 API（家庭功能）**：

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/households | 获取用户所属的家庭列表 |
| POST | /api/households | 创建新家庭 |
| GET | /api/households/:id | 获取家庭详情 |
| PUT | /api/households/:id | 更新家庭信息 |
| DELETE | /api/households/:id | 删除家庭（仅 Owner） |
| GET | /api/households/:id/members | 获取家庭成员列表 |
| POST | /api/households/:id/members | 邀请成员 |
| PUT | /api/households/:id/members/:member_id | 更新成员权限 |
| DELETE | /api/households/:id/members/:member_id | 移除成员 |
| GET | /api/households/:id/analytics | 家庭数据分析 |
| GET | /api/households/:id/analytics/summary | 家庭汇总数据 |
| GET | /api/households/:id/analytics/compare | 成员对比分析 |
| GET | /api/households/:id/budgets | 家庭预算列表 |
| POST | /api/households/:id/budgets | 创建家庭预算 |

---

## 5. 部署方案

### 5.1 Docker 架构

单一镜像包含：
- **Nginx**: 静态文件服务（前端）
- **FastAPI**: 后端 API 服务
- **SQLite**: 数据库文件（Volume 挂载）
- **配置**: 环境变量配置

### 5.2 Dockerfile

```dockerfile
FROM python:3.12-slim-bullseye

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 构建前端
COPY webui /app/webui
WORKDIR /app/webui
RUN npm install && npm run build

# 安装后端依赖
COPY app /app/app
COPY pyproject.toml /app
WORKDIR /app
RUN uv sync --frozen --no-cache

# 安装 Nginx
RUN apt-get update && apt-get install -y nginx

# 配置 Nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动脚本
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
```

### 5.3 docker-compose.yml

```yaml
version: '3.8'

services:
  money:
    image: money:latest
    container_name: money
    ports:
      - "8080:80"
    volumes:
      - money-data:/app/data
      - money-logs:/app/logs
    environment:
      - DATABASE_URL=sqlite:///data/money.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

volumes:
  money-data:
  money-logs:
```

---

## 6. 安全与隐私

### 6.1 数据安全
- SQLite 本地存储，数据不离开用户环境
- 可选的云备份功能（用户自主选择）
- 敏感数据加密存储（API Key、备份密码）

### 6.2 API 安全
- JWT Token 认证（如需多用户支持）
- Rate Limiting 防止滥用
- CORS 严格配置
- SQL 注入防护（FastAPI ORM）

### 6.3 AI 隐私
- AI 分析可在本地进行（可选本地模型）
- 上传云端数据匿名化处理
- 用户可完全关闭 AI 功能

---

## 7. 性能优化

### 7.1 前端优化
- 路由懒加载（减少初始加载）
- 组件缓存（Pinia 状态持久化）
- 图片懒加载（如有）
- Service Worker 缓存（离线支持）

### 7.2 后端优化
- 数据库查询优化（索引、聚合查询）
- API 响应缓存（Redis 可选）
- 分页加载（交易列表）
- 异步任务（AI 分析后台处理）

### 7.3 资源优化
- 前端资源压缩（Gzip）
- 图片压缩（WebP 格式）
- 代码分割（Vite）
- Tree Shaking

---

## 8. 测试策略

### 8.1 前端测试
- 单元测试（Vitest）
- E2E 测试（Playwright）
- 组件测试（Vue Test Utils）

### 8.2 后端测试
- API 测试（pytest）
- 数据库测试（SQLite 内存库）
- AI 服务 Mock 测试

### 8.3 集成测试
- Docker 集成测试
- 端到端工作流测试
- 性能基准测试

---

## 9. 监控与日志

### 9.1 日志
- 应用日志（FastAPI + Vue）
- 错误日志（Sentry 可选）
- 访问日志（Nginx）

### 9.2 监控指标
- API 响应时间
- 数据库查询性能
- 前端加载时间
- 用户活跃度

---

## 10. 未来扩展

### 10.1 多设备同步
- WebDAV 同步
- 云存储集成（自托管 Nextcloud）
- 端到端加密

### 10.2 导出导入
- Excel/CSV 导出（数据备份）
- ~~Excel/CSV 导入~~ (已在 P1 实现：支付宝/微信账单)
- OFX/QIF 格式支持
- 数据迁移工具
- 云备份（自托管 Nextcloud/WebDAV）

### 10.3 多用户支持
- 家庭账户
- 权限管理
- 协作记账

### 10.4 移动端增强
- ~~PWA 支持~~ (已在 P0 实现)
- 原生 App（可选，基于 PWA 封装）
- 高级离线记账功能
- 语音输入记账
- 推送通知（预算超支提醒）

---

## 11. 优先级排序

### P0（必须完成）
1. 基础记账系统（阶段1）
2. 移动端适配（响应式设计 + PWA）
3. 核心数据可视化（阶段2：总览+趋势）

### P1（重要）
4. 支付宝/微信支付数据导入（CSV/Excel）
5. 截图自动解析（OCR 识别）
6. 家庭多用户支持（家庭成员管理、数据合并）
7. 预算管理（阶段3）
8. 深度数据分析（阶段2：热力图、对比）

### P2（增强）
9. AI 智能分类（阶段4）
10. AI 消费建议（阶段4）
11. 桑基图资金流向展示
12. 看板截图分享

### P3（未来）
13. 多设备同步
14. 导出导入（Excel/CSV 导出）
15. 原生移动应用（基于 PWA 的可选扩展）

---

## 12. 风险与挑战

### 12.1 技术风险
- **AI 准确性**: 初期规则可能不够智能，需要大量用户反馈
- **OCR 准确性**: 截图识别准确率依赖图片质量，可能需要用户手动校正
- **性能**: 大量数据时可视化可能卡顿，需优化查询；移动端性能优化；家庭数据合并查询复杂度高
- **兼容性**: 不同浏览器的表现差异；不同移动设备的适配
- **支付平台格式变化**: 支付宝/微信账单格式可能更新，需要持续维护
- **数据一致性**: 多用户并发编辑可能导致数据冲突，需要版本控制和冲突解决

### 12.2 产品风险
- **用户习惯**: 记账工具需要坚持使用，如何提高留存
- **功能平衡**: 极简 vs 功能丰富，如何取舍
- **AI 成本**: OpenAI API 调用成本控制
- **家庭场景复杂度**: 多用户权限、数据可见性、隐私保护等复杂逻辑可能增加用户学习成本
- **数据隐私**: 家庭成员对个人数据隐私的期望不同，如何平衡透明度和隐私

### 12.3 缓解措施
- 分阶段上线，收集用户反馈
- 提供多种 AI 方案（本地/云端/规则）
- 优化查询性能，添加缓存；家庭数据合并使用预计算和缓存
- 游戏化元素提升用户粘性
- 家庭功能提供简化的向导式引导
- 隐私设置提供多种预设模板，降低配置复杂度
- 使用乐观锁或版本号解决并发冲突

---

## 13. 成功指标

### 13.1 技术指标
- API 响应时间 < 200ms
- 前端首屏加载 < 2s（桌面端）
- 移动端首屏加载 < 3s
- 支持 10,000+ 交易记录无性能问题
- 支持家庭数据合并查询（5个成员、10000条记录）< 500ms
- Docker 镜像大小 < 500MB
- OCR 识别准确率 > 90%
- 账单导入成功率 > 95%

### 13.2 产品指标
- 记账完成率 > 80%（一次记账成功率）
- AI 分类准确率 > 85%
- 截图记账使用率 > 40%
- 移动端用户占比 > 60%
- 家庭用户占比 > 30%（使用家庭功能的用户）
- 用户月留存率 > 30%
- 平均日活跃时间 > 2 分钟
- 家庭成员平均活跃数 > 2 人/家庭

---

## 14. 总结

Money 是一款定位清晰的个人/家庭记账工具，通过分阶段实现，从基础记账到 AI 智能化，逐步完善功能。技术栈成熟可靠，部署简单，适合个人或小团队快速开发和迭代。

**核心特性**：
- 移动优先设计，响应式适配全设备
- 支持支付宝/微信账单快速导入
- 截图自动识别，3秒完成记账
- AI 智能分类和建议
- 丰富的数据可视化洞察（含桑基图资金流向）
- 家庭多用户支持，数据合并展示和分析
- 看板截图分享功能
- 管理员可配置多个 AI 模型（OpenAI 兼容接口）
- 极简设计，零学习成本

**核心场景**：
- **个人记账**：快速记录日常收支，AI 辅助分类
- **家庭财务**：夫妻/家庭成员共同记账，合并查看家庭总览
- **数据导入**：一键导入支付宝/微信账单，截图识别自动录入
- **智能分析**：桑基图展示资金流向，看板截图分享

核心理念：**极简设计 + AI 智能 + 数据驱动 + 移动优先 + 家庭协作 = 更好的理财体验**。

---

**文档版本**: v1.3
**最后更新**: 2026-03-14

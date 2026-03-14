# Money - 极简AI驱动个人记账工具

## 设计文档

**创建日期**: 2026-03-14
**最后更新**: 2026-03-14
**版本**: v1.1
**作者**: Sisyphus

## 变更日志

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

#### 3.6 前端组件
- **Dashboard.vue**: 仪表盘主页
- **TrendChart.vue**: 趋势图组件
- **PieChart.vue**: 饼图组件
- **Heatmap.vue**: 热力图组件
- **TimeRangeSelector.vue**: 时间范围选择器

#### 3.7 后端 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/analytics/summary | 总览数据（总收支、余额） |
| GET | /api/analytics/trends | 趋势数据（按时间段分组） |
| GET | /api/analytics/by-category | 分类统计 |
| GET | /api/analytics/heatmap | 热力图数据 |

#### 3.8 性能优化

```sql
-- 添加索引提升查询性能
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);
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
                      └──────────────┘              │
                                                    │ *   * │
                                                    ▼       │
                                          ┌─────────────┐
                                          │budget_alerts│
                                          ├─────────────┤
                                          │ id (PK)     │
                                          │ budget_id   │
                                          │ threshold   │
                                          │ triggered_at│
                                          │ status      │
                                          └─────────────┘
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
```

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
6. 预算管理（阶段3）
7. 深度数据分析（阶段2：热力图、对比）

### P2（增强）
8. AI 智能分类（阶段4）
9. AI 消费建议（阶段4）

### P3（未来）
10. 多设备同步
11. 导出导入（Excel/CSV 导出）
12. 原生移动应用（基于 PWA 的可选扩展）

---

## 12. 风险与挑战

### 12.1 技术风险
- **AI 准确性**: 初期规则可能不够智能，需要大量用户反馈
- **OCR 准确性**: 截图识别准确率依赖图片质量，可能需要用户手动校正
- **性能**: 大量数据时可视化可能卡顿，需优化查询；移动端性能优化
- **兼容性**: 不同浏览器的表现差异；不同移动设备的适配
- **支付平台格式变化**: 支付宝/微信账单格式可能更新，需要持续维护

### 12.2 产品风险
- **用户习惯**: 记账工具需要坚持使用，如何提高留存
- **功能平衡**: 极简 vs 功能丰富，如何取舍
- **AI 成本**: OpenAI API 调用成本控制

### 12.3 缓解措施
- 分阶段上线，收集用户反馈
- 提供多种 AI 方案（本地/云端/规则）
- 优化查询性能，添加缓存
- 游戏化元素提升用户粘性

---

## 13. 成功指标

### 13.1 技术指标
- API 响应时间 < 200ms
- 前端首屏加载 < 2s（桌面端）
- 移动端首屏加载 < 3s
- 支持 10,000+ 交易记录无性能问题
- Docker 镜像大小 < 500MB
- OCR 识别准确率 > 90%
- 账单导入成功率 > 95%

### 13.2 产品指标
- 记账完成率 > 80%（一次记账成功率）
- AI 分类准确率 > 85%
- 截图记账使用率 > 40%
- 移动端用户占比 > 60%
- 用户月留存率 > 30%
- 平均日活跃时间 > 2 分钟

---

## 14. 总结

Money 是一款定位清晰的个人记账工具，通过分阶段实现，从基础记账到 AI 智能化，逐步完善功能。技术栈成熟可靠，部署简单，适合个人或小团队快速开发和迭代。

**核心特性**：
- 移动优先设计，响应式适配全设备
- 支持支付宝/微信账单快速导入
- 截图自动识别，3秒完成记账
- AI 智能分类和建议
- 丰富的数据可视化洞察
- 极简设计，零学习成本

核心理念：**极简设计 + AI 智能 + 数据驱动 + 移动优先 = 更好的理财体验**。

---

**文档版本**: v1.0
**最后更新**: 2026-03-14

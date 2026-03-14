# Money - 极简AI驱动个人记账工具

## 设计文档

**创建日期**: 2026-03-14
**最后更新**: 2026-03-14
**版本**: v2.0
**作者**: Sisyphus

## 变更日志

**v2.0 (2026-03-14)**
- UI/UX 设计采用 Apple 风格：极致简洁、流畅动画、圆润设计
- 新增软删除功能，所有删除操作均可恢复，便于查账核对
- 完善手动录入功能，优化表单体验
- 新增回收站功能，查看和恢复已删除记录
- 优化移动端交互，参考 iOS 原生体验

**v1.9 (2026-03-14)**
- 新增自定义标签功能，用户可为交易添加标签（旅游、工资、紧急支出等）
- 新增时间段标签功能，可按时间段标记记录（春节、暑假、季度等）
- 支持标签筛选、统计和导出
- 标签支持颜色自定义和图标

**v1.8 (2026-03-14)**
- 新增文件原件保留功能，用户导入的支付宝/微信支付文件会保存原件
- 支持查看、下载、删除导入的原始文件
- 文件存储支持本地文件和 MinIO（对象存储）

**v1.7 (2026-03-14)**
- 新增 ASR（语音识别）支持，用户可通过语音输入快速记账
- 新增文本粘贴录入功能，支持从短信、聊天记录等复制粘贴后 AI 自动解析

**v1.6 (2026-03-14)**
- 新增多达 15 种 AI 模型服务提供商支持（OpenAI/DeepSeek/Gemini/Anthropic/Moonshot/Qwen/Zhipu/Ollama/OpenRouter/MiniMax/NVIDIA/vLLM 等）
- 恢复 Playwright 后端渲染方案（作为高质量截图的可选方案）
- 支持用户选择前端或后端截图方案

**v1.5 (2026-03-14)**
- 优化看板截图分享方案：移除 Playwright 后端渲染，改用前端 html2canvas
- 降低项目复杂性，减少部署依赖

**v1.4 (2026-03-14)**
- 新增灵活的数据库配置（SQLite/MySQL/PostgreSQL）
- 新增存储后端配置选项（本地文件/MinIO/RustFS）
- 新增缓存加速选项（Redis）
- 优化部署向导，支持用户选择基础设施组件

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

采用前后端分离架构，Docker 单一镜像部署，支持灵活的基础设施配置：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Docker Compose / K8s 集群                        │
│  ┌────────────┐    ┌─────────────┐    ┌──────────────────────────────┐   │
│  │   Nginx   │───▶│  FastAPI    │────▶│   数据库 (可选)             │   │
│  │ (静态文件) │    │  (后端API)  │    │  ├─ SQLite (默认，本地文件)  │   │
│  └────────────┘    └──────┬──────┘    │  ├─ MySQL (可选)            │   │
│                           │            │  └─ PostgreSQL (可选)       │   │
│                    ┌──────▼──────┐    └──────────────────────────────┘   │
│                    │   Redis     │    ┌──────────────────────────────┐   │
│                    │  (可选缓存) │    │   存储后端 (可选)          │   │
│                    └─────────────┘    │  ├─ 本地文件 (默认)        │   │
│                           │         │  ├─ MinIO (对象存储)       │   │
│                    ┌──────▼──────┐    │  └─ RustFS (分布式)       │   │
│                    │  AI引擎     │    └──────────────────────────────┘   │
│                    │ (OpenAI等)  │                                      │
│                    └─────────────┘                                      │
│                                                                   │   │
│                  前端截图 (html2canvas)                              │   │
│                  ├─ 无需后端支持                                      │   │
│                  └─ 浏览器端直接生成                                   │   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

#### 前端
- **框架**: Vue 3.5 + TypeScript
- **构建**: Vite 6
- **路由**: Vue Router 4
- **状态管理**: Pinia 3
- **图表库**: ECharts
- **UI 设计风格**: Apple Design（Human Interface Guidelines）
- **UI 组件**: 自定义组件库（保持极简）
- **移动端适配**: 响应式设计 + PWA 支持
- **文件上传**: 文件导入/截图上传组件
- **动画库**: GSAP / VueUse（流畅过渡动画）

#### UI/UX 设计原则（Apple 风格）

**核心原则**：
- **极简主义**：界面清爽，留白充足，突出核心功能
- **一致性**：统一的视觉语言、交互模式、命名规范
- **清晰性**：明确的信息层级、清晰的标签、易懂的图标
- **流畅性**：自然的动画过渡、快速的响应、流畅的手势

**色彩系统**：

```css
/* Apple 风格色彩系统 */
:root {
  /* 主色调 - 蓝色系 */
  --color-primary: #007AFF;
  --color-primary-light: #5AC8FA;
  --color-primary-dark: #0051D5;

  /* 中性色 */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F2F2F7;
  --color-bg-tertiary: #E5E5EA;

  /* 文本色 */
  --color-text-primary: #000000;
  --color-text-secondary: #8E8E93;
  --color-text-tertiary: #C7C7CC;

  /* 功能色 */
  --color-success: #34C759;  /* 绿色 */
  --color-warning: #FF9500;  /* 橙色 */
  --color-error: #FF3B30;   /* 红色 */
  --color-info: #5AC8FA;    /* 青色 */
}
```

**字体系统**：

```css
/* Apple 字体栈 */
:root {
  --font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

**圆角系统**：

```css
/* Apple 圆角规范 */
:root {
  --radius-sm: 8px;    /* 小按钮、标签 */
  --radius-md: 12px;   /* 卡片、输入框 */
  --radius-lg: 16px;   /* 模态框、面板 */
  --radius-xl: 20px;   /* 大卡片 */
  --radius-2xl: 28px;  /* 全屏卡片 */
}
```

**阴影系统**：

```css
/* Apple 柔和阴影 */
:root {
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.15);
  --shadow-xl: 0 16px 32px rgba(0, 0, 0, 0.2);
}
```

**动画系统**：

```css
/* Apple 流畅动画 */
:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;

  --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-spring: cubic-bezier(0.25, 0.1, 0.25, 1.0);
}
```

**组件设计规范**：

1. **卡片组件**：
   - 背景纯白，圆角 12-16px
   - 轻微阴影（shadow-sm）
   - 内边距 16-20px
   - hover 效果：轻微上浮 + 阴影加深

2. **按钮组件**：
   - 主按钮：蓝色背景，白色文字，圆角 8-12px
   - 次按钮：灰色背景，黑色文字
   - 图标按钮：圆形或方形，尺寸 44x44px（触摸友好）
   - 点击反馈：缩小到 0.95 然后恢复（按压效果）

3. **输入框组件**：
   - 纯白背景，浅灰边框（#E5E5EA）
   - Focus 状态：蓝色边框 + 蓝色阴影
   - Error 状态：红色边框 + 错误提示
   - Label：小字号，灰色，位于输入框上方

4. **列表组件**：
   - 分组展示，组间距 24px
   - 列表项高度 44-56px（触摸友好）
   - 分隔线：1px 浅灰线（#E5E5EA），两端留白
   - 左滑操作：显示删除/编辑按钮（iOS 风格）

5. **模态框组件**：
   - 半透明黑色背景遮罩（rgba(0,0,0,0.4)）
   - 从底部滑入（底部弹窗）或 从中心弹出
   - 圆角 20-28px（iOS 风格）
   - 滑动关闭支持（向下拖动）

6. **标签页组件**：
   - 水平滚动的胶囊形标签
   - 选中状态：蓝色背景，白色文字
   - 未选中状态：浅灰背景，黑色文字
   - 过渡动画：300ms， ease-in-out

7. **图标组件**：
   - SF Symbols 风格图标（圆润、简洁）
   - 尺寸规范：16px / 24px / 32px / 48px
   - 颜色：中性灰或功能色
   - 支持填充和描边两种风格

**布局规范**：

```css
/* Apple 安全区域适配 */
.container {
  padding-left: env(safe-area-inset-left, 16px);
  padding-right: env(safe-area-inset-right, 16px);
  padding-top: env(safe-area-inset-top, 16px);
  padding-bottom: env(safe-area-inset-bottom, 16px);
}

/* 网格系统 */
.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

/* Flexbox 布局 */
.flex {
  display: flex;
  align-items: center;
  gap: 12px;
}
```

**移动端优化**：

1. **触摸目标**：
   - 最小点击区域：44x44px
   - 按钮高度：44-56px
   - 列表项高度：56px

2. **手势支持**：
   - 左滑删除（交易列表）
   - 下拉刷新（交易列表）
   - 长按显示上下文菜单
   - 双击快速操作

3. **响应式断点**：
   ```css
   @media (max-width: 640px) {
     /* 移动端布局 */
   }
   @media (min-width: 641px) and (max-width: 1024px) {
     /* 平板布局 */
   }
   @media (min-width: 1025px) {
     /* 桌面端布局 */
   }
   ```

4. **暗黑模式**：
   ```css
   @media (prefers-color-scheme: dark) {
     :root {
       --color-bg-primary: #000000;
       --color-bg-secondary: #1C1C1E;
       --color-text-primary: #FFFFFF;
       --color-text-secondary: #98989D;
     }
   }
   ```

#### 后端
- **框架**: FastAPI (Python 3.12+)
- **数据库**: SQLite（默认） / MySQL（可选） / PostgreSQL（可选）
- **缓存**: Redis（可选，加速查询和会话）
- **存储**: 本地文件（默认） / MinIO（可选） / RustFS（可选）
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
- **标签管理**: 标签增删改、颜色和图标自定义
- **时间段标签**: 创建时间段标签（春节、暑假等）
- **截图上传**: 支付截图识别组件
- **文件导入**: CSV/Excel 导入组件
- **移动端适配**: 响应式布局、FAB 快速记账按钮、底部导航栏
- **标签筛选器**: 按标签筛选交易
- **标签统计**: 按标签统计收支

#### 3.3 后端 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/transactions | 创建交易 |
| GET | /api/transactions | 获取交易列表（支持筛选、标签过滤） |
| PUT | /api/transactions/:id | 更新交易（包括标签） |
| DELETE | /api/transactions/:id | 软删除交易（移入回收站） |
| POST | /api/transactions/:id/restore | 恢复已删除的交易 |
| POST | /api/transactions/quick | 快速手动记账（简化参数） |
| GET | /api/categories | 获取分类列表 |
| POST | /api/categories | 创建分类 |
| DELETE | /api/categories/:id | 软删除分类（移入回收站） |
| POST | /api/categories/:id/restore | 恢复已删除的分类 |
| GET | /api/recycle-bin | 获取回收站列表 |
| DELETE | /api/recycle-bin/:id | 永久删除回收站项目 |
| POST | /api/recycle-bin/restore/:id | 恢复回收站项目 |
| POST | /api/recycle-bin/empty | 清空回收站 |
| GET | /api/recycle-bin/settings | 获取回收站设置（自动清理天数） |
| PUT | /api/recycle-bin/settings | 更新回收站设置 |

#### 3.3.1 软删除设计

**核心功能**：
- 所有删除操作均为软删除，不会永久删除数据
- 删除的项目移入回收站，保留 30 天（可配置）
- 支持从回收站恢复任何已删除项目
- 支持批量恢复和批量永久删除
- 自动清理过期项目（后台任务）

**软删除策略**：

| 项目类型 | 软删除行为 | 恢复行为 | 级联删除 |
|---------|------------|----------|---------|
| **交易** | 标记 `is_deleted=TRUE`，记录删除时间 | 取消删除标记，恢复原数据 | 无级联 |
| **分类** | 标记 `is_deleted=TRUE`，已关联交易保留 | 取消删除标记 | 无级联 |
| **预算** | 标记 `is_deleted=TRUE`，相关告警保留 | 取消删除标记 | 级联删除告警 |
| **标签** | 标记 `is_deleted=TRUE` | 取消删除标记 | 级联删除交易-标签关联 |

**回收站 API 详情**：

```json
// GET /api/recycle-bin?type=transaction&limit=20
{
  "items": [
    {
      "id": 1,
      "item_type": "transaction",
      "item_id": 12345,
      "item_data": {
        "id": 12345,
        "amount": 45.00,
        "type": "expense",
        "category_name": "餐饮",
        "date": "2026-03-14",
        "note": "麦当劳午餐"
      },
      "deleted_by": {
        "id": 1,
        "username": "张三",
        "display_name": "张三"
      },
      "deleted_at": "2026-03-14T15:30:00Z",
      "expires_at": "2026-04-13T15:30:00Z",
      "can_restore": true,
      "days_until_expired": 30
    }
  ],
  "total": 5,
  "has_expired": false
}
```

**恢复操作**：

```python
# 恢复单个项目
POST /api/recycle-bin/restore/1
{
  "item_type": "transaction",
  "item_id": 12345
}

# 响应
{
  "success": true,
  "message": "已恢复交易记录",
  "restored_item": {
    "id": 12345,
    "is_deleted": false,
    "deleted_at": null
  }
}
```

**永久删除**：

```python
# 永久删除（无法恢复）
DELETE /api/recycle-bin/1
{
  "confirm": true  # 需要确认操作
}

# 响应
{
  "success": true,
  "message": "已永久删除该记录",
  "permanently_deleted_at": "2026-03-14T16:00:00Z"
}
```

**回收站设置**：

```json
{
  "auto_cleanup_days": 30,      // 自动清理天数
  "max_items": 1000,          // 回收站最大容量
  "enable_auto_cleanup": true   // 是否启用自动清理
}
```

**批量操作**：

```python
# 批量恢复
POST /api/recycle-bin/restore-batch
{
  "item_ids": [1, 2, 3, 4, 5]
}

// 批量永久删除
DELETE /api/recycle-bin/batch
{
  "item_ids": [1, 2, 3],
  "confirm": true
}

// 清空回收站
POST /api/recycle-bin/empty
{
  "confirm": true,
  "empty_expired_only": false  // 是否只清空过期项目
}
```

#### 3.3.2 手动录入功能

**功能特性**：
- 极简表单设计，3 步完成记账
- 智能默认值（日期默认今天、时间默认当前）
- 快速选择器（分类、标签、支付方式）
- 金额输入优化（大字体、快速键盘适配）
- 支持快捷键（Ctrl+Enter 提交、Esc 取消）
- 自动保存草稿（未完成表单本地缓存）
- 智能联想（基于历史记录推荐分类、备注）

**表单设计**（Apple 风格）：

```
┌─────────────────────────────────────────────┐
│  新建交易                            ✕  │
├─────────────────────────────────────────────┤
│                                       │
│  收入 / 支出  [分段控制]             │
│  ◉ 支出   ○ 收入                      │
│                                       │
│  ¥ 45.00                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%    │
│  金额                                  │
│                                       │
│  餐饮                 ▼              │
│  分类                                  │
│                                       │
│  🍽️ 午餐、麦当劳汉堡套餐                │
│  备注 (可选)                           │
│                                       │
│  ┌──────┐  ┌──────┐                  │
│  │今天  │  │12:30 │                  │
│  └──────┘  └──────┘                  │
│  日期        时间                       │
│                                       │
│  [🔖 旅游] [🏠 房租] [+ 标签]    │
│  标签                                  │
│                                       │
│         [取消]           [保存]        │
│                                       │
└─────────────────────────────────────────────┘
```

**快速记账接口**：

```python
POST /api/transactions/quick

# 简化参数（适合键盘输入）
{
  "amount": 45,
  "category_id": 1,
  "note": "麦当劳"
}

# 默认值
- type: 'expense'  // 默认支出
- date: 今天
- time: 当前时间
- tags: []  // 空标签
```

**智能联想**：

```python
GET /api/transactions/suggestions?prefix=麦当劳

# 响应
{
  "suggestions": [
    {
      "text": "麦当劳汉堡套餐",
      "category_id": 1,
      "amount": 45.00,
      "confidence": 0.95,
      "frequency": 15
    },
    {
      "text": "麦当劳早餐",
      "category_id": 1,
      "amount": 25.00,
      "confidence": 0.88,
      "frequency": 8
    }
  ]
}
```

**前端组件**：

- **TransactionForm.vue**: 交易录入表单（Apple 风格）
- **QuickRecordModal.vue`: 快速记账弹窗
- **AmountInput.vue`: 金额输入组件（大字体、滑块）
- **CategoryPicker.vue`: 分类选择器（分组、搜索）
- **TagPicker.vue`: 标签选择器（多选、颜色预览）
- **DateTimePicker.vue`: 日期时间选择器
- **AutoCompleteInput.vue`: 智能联想输入框
- **RecycleBin.vue`: 回收站列表
- **RecycleBinItem.vue`: 回收站项目卡片
- **RecycleBinSettings.vue`: 回收站设置

**删除确认弹窗**（iOS 风格）：

```vue
<template>
  <div class="delete-alert">
    <div class="alert-icon">🗑️</div>
    <h3 class="alert-title">删除交易</h3>
    <p class="alert-message">
      此操作将移入回收站，可在 30 天内恢复。
    </p>
    <div class="alert-actions">
      <button class="btn-cancel">取消</button>
      <button class="btn-delete">删除</button>
    </div>
  </div>
</template>
```
| GET | /api/tags | 获取标签列表 |
| POST | /api/tags | 创建标签 |
| PUT | /api/tags/:id | 更新标签 |
| DELETE | /api/tags/:id | 删除标签 |
| GET | /api/time-periods | 获取时间段标签列表 |
| POST | /api/time-periods | 创建时间段标签 |
| PUT | /api/time-periods/:id | 更新时间段标签 |
| DELETE | /api/time-periods/:id | 删除时间段标签 |
| GET | /api/analytics/by-tag | 按标签统计收支 |
| POST | /api/transactions/:id/tags | 为交易添加标签 |
| DELETE | /api/transactions/:id/tags/:tag_id | 移除交易的标签 |

#### 3.3.1 标签管理功能

**功能特性**：
- 自定义标签（用户可创建任意标签）
- 标签类型：普通标签、时间段标签
- 标签属性：名称、颜色、图标、描述
- 标签关联：一个交易可关联多个标签
- 标签筛选：按标签筛选交易
- 标签统计：按标签统计收支情况
- 标签导出：按标签导出交易记录

**标签类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| **普通标签** | 用户自定义的标签 | 旅游、工资、紧急支出、日常消费 |
| **时间段标签** | 基于时间段的标签 | 2026年春节、2026年Q1、2026年暑假、2026年12月 |
| **系统标签** | 系统预置的标签 | 本月、上月、本季、本年 |

**标签属性**：

```json
{
  "id": 1,
  "name": "旅游",
  "type": "custom",  // 'custom', 'time_period', 'system'
  "color": "#FF5733",
  "icon": "plane",
  "description": "旅游相关支出",
  "created_by": 1,  // 创建者用户 ID
  "is_public": true,  // 是否对家庭成员公开
  "transaction_count": 15,  // 关联的交易数量
  "created_at": "2026-03-14T10:00:00Z"
}
```

**时间段标签示例**：

```json
{
  "name": "2026年春节",
  "type": "time_period",
  "color": "#E91E63",
  "icon": "celebration",
  "description": "2026年春节期间的消费",
  "period": {
    "start_date": "2026-01-28",
    "end_date": "2026-02-03",
    "type": "custom"  // 'custom', 'monthly', 'quarterly', 'yearly'
  }
}

{
  "name": "2026年Q1",
  "type": "time_period",
  "color": "#9C27B0",
  "icon": "calendar",
  "description": "2026年第一季度",
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "type": "quarterly"
  }
}
```

**前端组件**：

- **TagList.vue**: 标签列表展示
- **TagForm.vue`: 标签创建/编辑表单
- **TagPicker.vue`: 标签选择器（多选）
- **TagColorPicker.vue`: 标签颜色选择器
- **TagIconPicker.vue`: 标签图标选择器
- **TimePeriodForm.vue`: 时间段标签创建表单
- **TransactionTagList.vue`: 交易的标签展示
- **TagFilter.vue`: 标签筛选器
- **TagStats.vue`: 标签统计视图
- **TagCloud.vue`: 标签云视图（展示高频标签）

**标签颜色方案**：

预设颜色库（用户可自定义）：
```json
{
  "red": "#F44336",
  "pink": "#E91E63",
  "purple": "#9C27B0",
  "indigo": "#673AB7",
  "blue": "#2196F3",
  "cyan": "#00BCD4",
  "teal": "#009688",
  "green": "#4CAF50",
  "lime": "#CDDC39",
  "yellow": "#FFEB3B",
  "orange": "#FF9800",
  "brown": "#795548",
  "grey": "#9E9E9E"
}
```

**标签图标方案**：

预设图标库（用户可自定义）：
```json
{
  "salary": "💰",
  "travel": "✈️",
  "food": "🍽️",
  "shopping": "🛒",
  "transport": "🚗",
  "entertainment": "🎬",
  "health": "🏥",
  "education": "📚",
  "emergency": "⚠️",
  "celebration": "🎉"
}
```

#### 3.3.1 支付宝/微信支付数据导入

**功能特性**：
- 支持支付宝/微信账单 CSV/Excel 文件导入
- 自动解析支付平台账单格式
- 智能匹配分类和金额
- 批量导入进度显示
- 导入数据校验（去重、异常值检测）
- **保留导入文件原件**：用户可以随时查看和下载原始文件
- **文件去重检测**：基于文件哈希避免重复导入同一文件
- **文件存储管理**：支持本地文件和 MinIO 对象存储

**技术实现**：
- 后端使用 `pandas` 解析 CSV/Excel
- 支付宝账单格式识别（标准 CSV 格式）
- 微信账单格式识别（标准 CSV 格式）
- 数据清洗和标准化
- AI 辅助分类（基于备注和商户名称）
- **文件上传和存储**：使用 StorageBackend 适配层
- **文件哈希计算**：SHA256 计算文件哈希用于去重
- **文件分块上传**：大文件支持分块上传（可选）

**后端 API**：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/import/parse | 解析上传的账单文件 |
| POST | /api/import/preview | 预览导入数据（未保存） |
| POST | /api/import/confirm | 确认导入数据到数据库 |
| GET | /api/import/history | 导入历史记录 |
| GET | /api/import/files/:id | 下载导入的原始文件 |
| DELETE | /api/import/files/:id | 删除导入的原始文件 |
| GET | /api/import/files/:id/info | 获取文件信息（大小、类型等） |

**文件保留策略**：

1. **文件上传流程**：
   ```
   用户上传文件 → 计算文件哈希 → 检查是否已存在 → 保存文件 → 记录到数据库
   ```

2. **文件存储位置**：
   - **本地文件**：`/app/data/imports/{user_id}/{year}/{month}/{file_hash}.{ext}`
   - **MinIO**：`imports/{user_id}/{year}/{month}/{file_hash}.{ext}`

3. **文件保留规则**：
   - 默认永久保留（除非用户手动删除）
   - 提供"清理旧文件"功能（可配置保留时间）
   - 文件删除时仅删除引用，保留文件直到清理任务执行
   - 支持批量删除和导出文件列表

4. **文件去重逻辑**：
   ```python
   # 计算文件哈希
   file_hash = hashlib.sha256(file_content).hexdigest()

   # 检查是否已存在
   existing = db.query(import_records).filter_by(
       file_hash=file_hash,
       user_id=user_id
   ).first()

   if existing:
       raise FileAlreadyExistsError("文件已导入，无需重复上传")
   ```

**前端组件**：
- **ImportFileUpload.vue**: 文件上传组件（拖拽上传、点击上传）
- **ImportProgress.vue`: 导入进度条
- **ImportPreview.vue`: 导入预览表格
- **ImportHistory.vue`: 导入历史列表
- **ImportFileList.vue`: 已导入文件列表（查看/下载/删除）
- **FileViewer.vue`: 文件预览（CSV/Excel 在线预览）

**新增依赖**：

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
    "minio>=7.2.0",             # MinIO 客户端（可选）
]
```

**文件存储适配层**：

```python
# app/storage/import_storage.py
class ImportStorage:
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend

    async def save_import_file(
        self,
        user_id: int,
        file: UploadFile,
        file_type: str
    ) -> dict:
        # 计算文件哈希
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        # 生成存储路径
        date = datetime.now()
        path = f"imports/{user_id}/{date.year}/{date.month}/{file_hash}{Path(file.filename).suffix}"

        # 保存文件
        file_url = await self.storage.save(path, BytesIO(content))

        # 计算文件大小
        file_size = len(content)

        return {
            "file_name": file.filename,
            "file_path": path,
            "file_hash": file_hash,
            "file_size": file_size,
            "storage_type": self.storage.__class__.__name__,
            "file_url": file_url
        }

    async def get_import_file(self, file_path: str) -> BinaryIO:
        return await self.storage.get(file_path)

    async def delete_import_file(self, file_path: str) -> bool:
        return await self.storage.delete(file_path)
```

**文件管理界面**：

展示字段：
- 文件名
- 文件类型（支付宝/微信/Excel/CSV）
- 文件大小
- 导入时间
- 导入的交易数量
- 文件哈希（用于验证）
- 操作按钮（下载、删除、查看详情）

批量操作：
- 批量下载（打包成 ZIP）
- 批量删除
- 按时间范围筛选
- 按文件类型筛选

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
  user_id INTEGER,
  household_id INTEGER,
  is_deleted BOOLEAN DEFAULT FALSE,  -- 软删除标记
  deleted_at TIMESTAMP,            -- 删除时间
  deleted_by INTEGER,             -- 删除者用户 ID
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
  FOREIGN KEY (category_id) REFERENCES categories(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (household_id) REFERENCES households(id),
  FOREIGN KEY (deleted_by) REFERENCES users(id)
);

-- 导入记录表
CREATE TABLE import_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(20) NOT NULL,  -- 'alipay', 'wechat', 'excel', 'csv'
  file_path VARCHAR(500),           -- 文件存储路径
  file_size BIGINT DEFAULT 0,        -- 文件大小（字节）
  file_hash VARCHAR(64),            -- 文件 SHA256 哈希（用于去重）
  storage_type VARCHAR(20) DEFAULT 'local',  -- 'local', 'minio'
  import_count INTEGER NOT NULL,   -- 导入的交易数量
  skip_count INTEGER DEFAULT 0,     -- 跳过的数量（重复或无效）
  status VARCHAR(20) NOT NULL,     -- 'pending', 'completed', 'failed'
  error_message TEXT,
  user_id INTEGER NOT NULL,        -- 用户 ID
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 导入记录索引
CREATE INDEX idx_import_records_user ON import_records(user_id);
CREATE INDEX idx_import_records_file_hash ON import_records(file_hash);
CREATE INDEX idx_import_records_created_at ON import_records(created_at);

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

#### 3.7.1 前端截图分享（无需后端支持）

使用 html2canvas 在浏览器端直接生成截图：
- 无需后端 API 支持
- 用户体验更流畅（即时生成）
- 不增加部署复杂性

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

**方案 A（推荐）：前端 Canvas 导出**
- 使用 html2canvas 前端导出
- 无需后端支持
- 直接在浏览器端生成图片
- 支持下载和分享

**方案 B：SVG 导出**
- 将 ECharts 图表导出为 SVG
- 可缩放不失真
- 文件体积小

**实现细节（方案 A）**：

前端依赖：
```json
// package.json
{
  "dependencies": {
    "html2canvas": "^1.4.1",
    "file-saver": "^2.0.5"
  }
}
```

截图生成流程：
1. 用户点击"分享看板"按钮
2. 前端调用 html2canvas 捕获仪表盘区域
3. 生成 Canvas 图片
4. 转换为 PNG/PNG 格式
5. 提供下载或直接分享

截图配置：
```typescript
{
  "useCORS": true,
  "allowTaint": true,
  "scale": 2,  // 高分辨率
  "backgroundColor": "#ffffff"
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
- 支持录入多个 AI 服务提供商（15+ 种主流提供商）
- 每个服务可配置多个模型
- 统一的 OpenAI 兼容接口（适配绝大多数提供商）
- 管理员可切换默认使用的模型
- 支持模型优先级和降级策略（主模型失败时自动切换）
- 支持本地部署（Ollama、vLLM、本地模型服务）

**支持的 AI 服务提供商**（15+ 种）：

| 提供商 | 类型 | Base URL | 特点 |
|---------|------|----------|------|
| **OpenAI** | 商业 | `https://api.openai.com/v1` | GPT-4o/GPT-3.5，最成熟 |
| **DeepSeek** | 商业 | `https://api.deepseek.com` | 深度求索，高性价比中文模型 |
| **Google Gemini** | 商业 | `https://generativelanguage.googleapis.com/v1beta` | Google 最新大模型，多模态支持 |
| **Anthropic** | 商业 | `https://api.anthropic.com` | Claude 系列模型，长文本优秀 |
| **Moonshot** | 商业 | `https://api.moonshot.cn/v1` | 月之暗面，中文优化 |
| **Qwen** | 商业 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 通义千问，阿里云大模型 |
| **Zhipu** | 商业 | `https://open.bigmodel.cn/api/paas/v4` | 智谱 GLM，开源社区活跃 |
| **Ollama** | 本地 | `http://localhost:11434/v1` | 本地部署，支持多种开源模型 |
| **OpenRouter** | 商业 | `https://openrouter.ai/api/v1` | 模型聚合平台，一站式访问 |
| **MiniMax** | 商业 | `https://api.minimax.chat/v1` | 国内服务商，中文友好 |
| **NVIDIA** | 商业 | `https://integrate.api.nvidia.com/v1` | NVIDIA 托管模型，高性能 |
| **vLLM** | 本地 | 自定义 | 本地部署，高性能推理引擎 |
| **Azure OpenAI** | 商业 | 自定义 | 企业级 OpenAI 托管 |
| **自定义/兼容接口** | 自定义 | 自定义 | 任何兼容 OpenAI API 格式的服务 |

**提供商配置详情**：

```json
{
  "openai": {
    "name": "OpenAI",
    "provider_type": "openai",
    "base_url": "https://api.openai.com/v1",
    "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "o1-preview"]
  },
  "deepseek": {
    "name": "DeepSeek",
    "provider_type": "deepseek",
    "base_url": "https://api.deepseek.com",
    "models": ["deepseek-chat", "deepseek-coder"]
  },
  "gemini": {
    "name": "Google Gemini",
    "provider_type": "gemini",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "models": ["gemini-2.0-flash-exp", "gemini-2.5-pro-exp", "gemini-exp"]
  },
  "anthropic": {
    "name": "Anthropic Claude",
    "provider_type": "anthropic",
    "base_url": "https://api.anthropic.com/v1",
    "models": ["claude-3-5-sonnet", "claude-3-5-haiku", "claude-3-opus"]
  },
  "moonshot": {
    "name": "Moonshot",
    "provider_type": "moonshot",
    "base_url": "https://api.moonshot.cn/v1",
    "models": ["moonshot-v1-128k", "moonshot-v1-8k"]
  },
  "qwen": {
    "name": "Qwen (通义千问)",
    "provider_type": "qwen",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "models": ["qwen-max", "qwen-plus", "qwen-turbo"]
  },
  "zhipu": {
    "name": "Zhipu AI (智谱)",
    "provider_type": "zhipu",
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "models": ["glm-4-plus", "glm-4-air", "glm-4-flash", "glm-4v-flash"]
  },
  "ollama": {
    "name": "Ollama",
    "provider_type": "ollama",
    "base_url": "http://localhost:11434/v1",
    "models": ["llama3.1", "mistral", "qwen2.5", "deepseek-coder"],
    "is_local": true
  },
  "openrouter": {
    "name": "OpenRouter",
    "provider_type": "openrouter",
    "base_url": "https://openrouter.ai/api/v1",
    "models": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "deepseek/deepseek-chat"]
  },
  "minimax": {
    "name": "MiniMax",
    "provider_type": "minimax",
    "base_url": "https://api.minimax.chat/v1",
    "models": ["abab6.5s-chat", "abab5.5-chat"]
  },
  "nvidia": {
    "name": "NVIDIA NIM",
    "provider_type": "nvidia",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "models": ["meta/llama-3.1-405b-instruct", "mistralai/mistral-large"]
  },
  "vllm": {
    "name": "vLLM",
    "provider_type": "vllm",
    "base_url": "http://localhost:8000/v1",
    "models": ["custom-model"],
    "is_local": true
  }
}
```

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

#### 3.18 ASR 语音识别录入

**功能特性**：
- 支持语音输入记账（支持多语言）
- 自动识别语音中的金额、日期、分类、备注
- 实时语音转文字反馈
- 支持长语音录音和连续识别
- 自动结构化提取交易数据

**技术实现**：
- 前端使用浏览器 Web Speech API（零成本）
- 后端集成专业 ASR 服务（高精度）
- ASR 文本传递给 LLM 进行结构化提取

**ASR 服务提供商**：

| 提供商 | Base URL | 特点 |
|---------|----------|------|
| **OpenAI Whisper** | `https://api.openai.com/v1` | 业界最准确，多语言优秀 |
| **Google Speech-to-Text** | `https://speech.googleapis.com/v1` | Google 技术，实时性好 |
| **Azure Speech Service** | 自定义 | 微软企业级，支持方言 |
| **阿里云语音识别** | `https://nls-meta.cn-shanghai.aliyuncs.com` | 中文优化，国内访问快 |
| **腾讯云语音识别** | `https://asr.tencentcloudapi.com` | 中文准确率高 |
| **百度语音识别** | `https://aip.baidubce.com/rpc/2.0/asr` | 中文识别，免费额度 |
| **DeepSeek ASR** | `https://api.deepseek.com` | DeepSeek 自研，高性价比 |
| **Vosk** | 本地 | 开源本地识别，隐私好 |
| **Kaldi** | 本地 | 开源本地识别，高精度 |

**前端组件**：
- **VoiceInputButton.vue**: 语音输入按钮（FAB 悬浮按钮）
- **VoiceRecorder.vue**: 语音录制器
- **VoiceTranscript.vue**: 语音转文字实时显示
- **VoiceSettings.vue**: 语音识别配置（语言选择、服务商选择）

**后端 API**：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/asr/upload | 上传音频文件并识别 |
| POST | /api/asr/stream | 流式语音识别（实时） |
| GET | /api/asr/providers | 获取可用的 ASR 服务商 |
| GET | /api/asr/languages | 获取支持的语言列表 |

**识别流程**：
```
用户语音 → ASR 服务 → 文本 → LLM 结构化提取 → 交易数据 → 自动填充表单
```

**识别示例**：

用户语音：*"今天中午在麦当劳花了四十五块钱吃了汉堡套餐"*

ASR 识别：*"今天中午在麦当劳花了四十五块钱吃了汉堡套餐"*

LLM 提取：
```json
{
  "amount": 45.00,
  "type": "expense",
  "category": "餐饮",
  "date": "2026-03-14",
  "time": "12:30",
  "note": "麦当劳汉堡套餐",
  "confidence": 0.95
}
```

**新增依赖**：

```python
# pyproject.toml
dependencies = [
    "openai>=1.0.0",              # Whisper ASR
    "aiohttp>=3.9.0",            # 异步 HTTP
    "pydub>=0.25.0",             # 音频处理
    "webrtcvad>=2.0.10",         # 语音活动检测
]
```

#### 3.19 文本粘贴智能录入

**功能特性**：
- 支持从任何来源复制粘贴文本（短信、聊天记录、邮件等）
- AI 自动识别粘贴文本中的交易信息
- 智能提取：金额、日期、商户、备注
- 支持批量粘贴（多条记录）
- 实时预览和编辑识别结果

**支持的文本来源**：
- 支付宝/微信支付成功通知短信
- 银行信用卡消费短信
- 支付账单详情文本
- 聊天记录中的消费信息
- 任何包含金额和日期的文本

**技术实现**：
- 文本预处理（清理格式、提取关键信息）
- LLM 进行结构化数据提取
- 正则表达式辅助识别（日期、金额、手机号等）

**前端组件**：
- **TextPasteInput.vue**: 文本粘贴输入框
- **PastePreview.vue**: 粘贴内容预览
- **PasteExtractResult.vue**: 提取结果展示
- **BatchPasteEditor.vue`: 批量粘贴编辑器

**后端 API**：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST |api/paste/parse | 解析粘贴的文本 |
| POST | /api/paste/confirm | 确认并批量导入解析的交易 |

**识别示例**：

**粘贴文本 1（支付宝）**：
```
【支付宝】您在肯德基（北京中关村店）消费35.50元，余额128.50元。2026-03-14 18:30
```

**提取结果**：
```json
{
  "source": "alipay",
  "transactions": [
    {
      "amount": 35.50,
      "type": "expense",
      "category": "餐饮",
      "merchant": "肯德基（北京中关村店）",
      "date": "2026-03-14",
      "time": "18:30",
      "note": "支付宝消费",
      "confidence": 0.98
    }
  ]
}
```

**粘贴文本 2（微信）**：
```
微信支付凭证
商户：星巴克咖啡（国贸店）
金额：42.00元
时间：2026-03-14 14:22
```

**提取结果**：
```json
{
  "source": "wechat",
  "transactions": [
    {
      "amount": 42.00,
      "type": "expense",
      "category": "餐饮",
      "merchant": "星巴克咖啡（国贸店）",
      "date": "2026-03-14",
      "time": "14:22",
      "note": "微信支付",
      "confidence": 0.97
    }
  ]
}
```

**批量粘贴示例**：
```
今天中午在麦当劳花了45元
下午在星巴克买了咖啡38元
晚上在超市购物128元
```

**批量提取结果**：
```json
{
  "source": "text",
  "transactions": [
    {
      "amount": 45.00,
      "type": "expense",
      "category": "餐饮",
      "date": "2026-03-14",
      "time": "12:00",
      "note": "麦当劳午餐",
      "confidence": 0.92
    },
    {
      "amount": 38.00,
      "type": "expense",
      "category": "餐饮",
      "date": "2026-03-14",
      "time": "15:00",
      "note": "星巴克咖啡",
      "confidence": 0.92
    },
    {
      "amount": 128.00,
      "type": "expense",
      "category": "购物",
      "date": "2026-03-14",
      "time": "19:00",
      "note": "超市购物",
      "confidence": 0.90
    }
  ]
}
```

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
                       │ household_id│              │
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
                                          ▲
                                          │ 1
                                          │
                           ┌──────────────┤ 1   *
                           │ asr_records  │◀──────┐
                           ├──────────────┤       │
                           │ id (PK)      │  *    1│
                           │ audio_path   │◀───────┘
                           │ transcript  │       │
                           │ provider_id │       │ ┌──────────────┐ 1   * ┌──────────────┐
                           │ confidence  │       │ │ai_providers  │◀──────│ ai_models     │
                           │ duration    │       │ ├──────────────┤       ├──────────────┤
                           │ created_at  │       │ │ id (PK)      │       │ id (PK)      │
                           └──────────────┘       │ │ name         │       │ provider_id   │
                                    ▲       │ │ provider_type│       │ model_name    │
                                    │ 1     │ │ base_url     │       │ max_tokens   │
                                    │       │ │ api_key      │       │ use_for      │
                                    │       │ │ is_active    │       │ is_default   │
                                    │       │ │ priority     │       └──────────────┘
                           ┌──────────┤       │ │ is_asr      │       │ is_llm       │
                           │ paste_   │       │ └──────────────┘       │ use_for      │
                           │ records  │       └──────────────┘
                           ├──────────┤
                           │ id (PK)  │
                           │ text     │
                           │ source   │
                           │ user_id  │
                           │ created_at│
                           └──────────┘
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

-- 回收站表（软删除记录）
CREATE TABLE recycle_bin (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_type VARCHAR(20) NOT NULL,  -- 'transaction', 'category', 'budget', 'tag'
  item_id INTEGER NOT NULL,            -- 原始项目 ID
  item_data TEXT,                     -- JSON 格式的项目原始数据
  deleted_by INTEGER NOT NULL,         -- 删除者用户 ID
  deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,                -- 自动清理过期时间（默认30天后）
  restored_at TIMESTAMP,               -- 恢复时间
  user_id INTEGER NOT NULL,            -- 所有者用户 ID
  household_id INTEGER,               -- 家庭 ID（如果是家庭项目）
  FOREIGN KEY (deleted_by) REFERENCES users(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (household_id) REFERENCES households(id)
);

-- 回收站索引
CREATE INDEX idx_recycle_bin_user ON recycle_bin(user_id);
CREATE INDEX idx_recycle_bin_household ON recycle_bin(household_id);
CREATE INDEX idx_recycle_bin_item ON recycle_bin(item_type, item_id);
CREATE INDEX idx_recycle_bin_expires_at ON recycle_bin(expires_at);

-- ASR 识别记录表
CREATE TABLE asr_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  audio_path VARCHAR(255),
  transcript TEXT NOT NULL,             -- ASR 识别的文本
  provider_id INTEGER,                    -- ASR 服务商 ID（可选）
  confidence_score DECIMAL(3, 2),     -- 识别置信度 0.00-1.00
  duration DECIMAL(5, 2),              -- 音频时长（秒）
  transaction_id INTEGER,                  -- 关联的交易ID（如果已创建）
  user_id INTEGER NOT NULL,               -- 用户ID
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (provider_id) REFERENCES ai_providers(id),
  FOREIGN KEY (transaction_id) REFERENCES transactions(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 文本粘贴记录表
CREATE TABLE paste_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,                   -- 粘贴的原始文本
  source VARCHAR(50),                   -- 文本来源（短信、聊天记录等）
  extracted_data TEXT,                   -- JSON 格式的提取结果
  transactions_count INTEGER DEFAULT 0,    -- 提取的交易数量
  user_id INTEGER NOT NULL,              -- 用户ID
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ASR 和粘贴相关索引
CREATE INDEX idx_asr_records_user ON asr_records(user_id);
CREATE INDEX idx_asr_records_created_at ON asr_records(created_at);
CREATE INDEX idx_paste_records_user ON paste_records(user_id);
CREATE INDEX idx_paste_records_created_at ON paste_records(created_at);
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

## 5. 基础设施配置

### 5.1 首次部署向导

应用首次启动时，展示配置向导让用户选择基础设施组件：

#### 5.1.1 数据库选择

**SQLite（默认）**
- ✅ 零配置，开箱即用
- ✅ 数据存储在本地文件 `/app/data/money.db`
- ✅ 适合个人和小家庭场景
- ❌ 不支持多实例并发写入

**MySQL（可选）**
- ✅ 支持高并发，适合大团队
- ✅ 成熟稳定，生态丰富
- ❌ 需要额外部署 MySQL 服务
- ❌ 配置相对复杂

**PostgreSQL（可选）**
- ✅ 功能强大，支持复杂查询
- ✅ 开源免费，性能优秀
- ❌ 需要额外部署 PostgreSQL 服务
- ❌ 资源占用较高

**配置示例**：
```yaml
# docker-compose.yml
services:
  money:
    environment:
      - DATABASE_TYPE=sqlite  # or mysql, postgresql
      - DATABASE_URL=sqlite:///data/money.db
      # MySQL 示例:
      # - DATABASE_URL=mysql+pymysql://user:password@mysql:3306/money
      # PostgreSQL 示例:
      # - DATABASE_URL=postgresql://user:password@postgres:5432/money

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_DATABASE=money
      - MYSQL_USER=money
      - MYSQL_PASSWORD=moneypass
    volumes:
      - mysql-data:/var/lib/mysql

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=money
      - POSTGRES_USER=money
      - POSTGRES_PASSWORD=moneypass
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

#### 5.1.2 存储后端选择

**本地文件（默认）**
- ✅ 零配置，开箱即用
- ✅ 数据存储在 `/app/data/`
- ✅ 适合个人和小团队
- ❌ 不支持分布式部署

**MinIO（可选）**
- ✅ S3 兼容的对象存储
- ✅ 支持分布式部署
- ✅ 高可用，可扩展
- ❌ 需要额外部署 MinIO 服务
- ❌ 配置相对复杂

**RustFS（可选）**
- ✅ 高性能分布式文件系统
- ✅ Rust 实现，性能优异
- ❌ 需要额外部署 RustFS
- ❌ 生态相对较新

**配置示例**：
```yaml
services:
  money:
    environment:
      - STORAGE_TYPE=local  # or minio, rustfs
      - STORAGE_PATH=/app/data
      # MinIO 示例:
      # - STORAGE_TYPE=minio
      # - MINIO_ENDPOINT=minio:9000
      # - MINIO_ACCESS_KEY=minioadmin
      # - MINIO_SECRET_KEY=minioadmin
      # - MINIO_BUCKET=money-files

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
```

#### 5.1.3 缓存选择

**无缓存（默认）**
- ✅ 零配置，部署简单
- ✅ 减少依赖
- ❌ 查询性能受数据库限制
- ❌ 高并发时可能有延迟

**Redis（可选）**
- ✅ 显著提升查询性能
- ✅ 支持会话缓存
- ✅ 支持数据预计算缓存
- ❌ 需要额外部署 Redis 服务
- ❌ 增加部署复杂度

**配置示例**：
```yaml
services:
  money:
    environment:
      - CACHE_TYPE=none  # or redis
      # Redis 示例:
      # - CACHE_TYPE=redis
      # - REDIS_URL=redis://redis:6379/0

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
```

### 5.2 数据库适配层

使用 SQLAlchemy + Alembic 实现数据库无关性：

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url():
    db_type = os.getenv("DATABASE_TYPE", "sqlite")
    if db_type == "sqlite":
        return "sqlite:///data/money.db"
    elif db_type == "mysql":
        return os.getenv("DATABASE_URL")
    elif db_type == "postgresql":
        return os.getenv("DATABASE_URL")
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Alembic 迁移支持多数据库
# alembic/env.py 中的 context.configure() 会自动适配
```

### 5.3 存储适配层

抽象存储接口，支持多种存储后端：

```python
# app/storage/base.py
from abc import ABC, abstractmethod
from typing import BinaryIO

class StorageBackend(ABC):
    @abstractmethod
    async def save(self, path: str, data: BinaryIO) -> str:
        pass

    @abstractmethod
    async def get(self, path: str) -> BinaryIO:
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        pass

# app/storage/local.py
class LocalStorage(StorageBackend):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    async def save(self, path: str, data: BinaryIO) -> str:
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data.read())
        return str(full_path)

# app/storage/minio.py
class MinioStorage(StorageBackend):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.client = Minio(endpoint, access_key, secret_key, secure=False)
        self.bucket = bucket

    async def save(self, path: str, data: BinaryIO) -> str:
        self.client.put_object(self.bucket, path, data, length=len(data.read()))
        return f"{endpoint}/{self.bucket}/{path}"
```

### 5.4 缓存适配层

使用 Redis 作为缓存后端：

```python
# app/cache.py
import redis
from typing import Optional

class CacheBackend:
    def __init__(self):
        self.client = None

    def init_redis(self, redis_url: str):
        self.client = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            return self.client.get(key)
        return None

    async def set(self, key: str, value: str, ttl: int = 3600):
        if self.client:
            self.client.setex(key, ttl, value)

    async def delete(self, key: str):
        if self.client:
            self.client.delete(key)
```

---

## 6. 部署方案

### 6.1 Docker 架构

单一镜像包含：
- **Nginx**: 静态文件服务（前端）
- **FastAPI**: 后端 API 服务
- **SQLite**: 数据库文件（默认，Volume 挂载）
- **配置**: 环境变量配置
- **可选依赖**: MySQL/PostgreSQL/Redis/MinIO（通过 docker-compose 添加）

### 6.2 Dockerfile

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

### 6.3 docker-compose.yml

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

## 7. 安全与隐私

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

## 8. 性能优化

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

## 9. 测试策略

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

## 10. 监控与日志

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

## 11. 未来扩展

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

## 12. 优先级排序

### P0（必须完成）
1. **UI/UX 设计**：Apple Design 风格，极致简洁，流畅动画
2. 基础记账系统（阶段1）
3. **软删除功能**：所有删除操作支持恢复，便于查账核对
4. 移动端适配（响应式设计 + PWA + iOS 原生体验）
5. 核心数据可视化（阶段2：总览+趋势）
6. **手动录入优化**：3 步完成记账，智能默认值

### P1（重要）
7. 支付宝/微信支付数据导入（CSV/Excel）
8. 截图自动解析（OCR 识别）
9. 家庭多用户支持（家庭成员管理、数据合并）
10. 预算管理（阶段3）
11. 深度数据分析（阶段2：热力图、对比）
12. 文本粘贴智能录入（从短信、聊天记录等复制粘贴）
13. ASR 语音识别录入（语音输入快速记账）
14. 自定义标签功能（时间段标签、颜色图标）

### P2（增强）
15. AI 智能分类（阶段4）
16. AI 消费建议（阶段4）
17. 桑基图资金流向展示
18. 看板截图分享（前端 html2canvas + 可选 Playwright）
19. 回收站管理（查看、恢复、批量操作）
20. 文件原件保留（导入的账单文件）

### P3（未来）
21. 多设备同步
22. 导出导入（Excel/CSV 导出）
23. 原生移动应用（基于 PWA 的可选扩展）

---

## 13. 风险与挑战

### 13.1 技术风险
- **AI 准确性**: 初期规则可能不够智能，需要大量用户反馈
- **OCR 准确性**: 截图识别准确率依赖图片质量，可能需要用户手动校正
- **ASR 准确性**: 语音识别准确率受环境噪音、口音、语速影响
- **文本解析准确率**: 粘贴文本格式多样，可能解析失败或识别错误
- **性能**: 大量数据时可视化可能卡顿，需优化查询；移动端性能优化；家庭数据合并查询复杂度高
- **兼容性**: 不同浏览器的表现差异；不同移动设备的适配；不同浏览器的 Web Speech API 支持程度
- **支付平台格式变化**: 支付宝/微信账单格式可能更新，需要持续维护
- **数据一致性**: 多用户并发编辑可能导致数据冲突，需要版本控制和冲突解决

### 13.2 产品风险
- **用户习惯**: 记账工具需要坚持使用，如何提高留存
- **功能平衡**: 极简 vs 功能丰富，如何取舍
- **AI 成本**: OpenAI API 调用成本控制；ASR 服务调用成本
- **家庭场景复杂度**: 多用户权限、数据可见性、隐私保护等复杂逻辑可能增加用户学习成本
- **数据隐私**: 家庭成员对个人数据隐私的期望不同，如何平衡透明度和隐私
- **语音录入接受度**: 用户可能不习惯语音记账，需要引导和优化体验

### 13.3 缓解措施
- 分阶段上线，收集用户反馈
- 提供多种 AI 方案（本地/云端/规则）
- 优化查询性能，添加缓存；家庭数据合并使用预计算和缓存
- 游戏化元素提升用户粘性
- 家庭功能提供简化的向导式引导
- 隐私设置提供多种预设模板，降低配置复杂度
- 使用乐观锁或版本号解决并发冲突
- ASR 提供多种服务商选择（本地/云端），降低成本和提升准确率
- 语音录入提供实时反馈和编辑功能，减少识别错误影响

---

## 14. 成功指标

### 14.1 技术指标
- API 响应时间 < 200ms
- 前端首屏加载 < 2s（桌面端）
- 移动端首屏加载 < 3s
- 支持 10,000+ 交易记录无性能问题
- 支持家庭数据合并查询（5个成员、10000条记录）< 500ms
- Docker 镜像大小 < 500MB
- OCR 识别准确率 > 90%
- ASR 识别准确率 > 85%
- 文本解析准确率 > 90%
- 账单导入成功率 > 95%

### 14.2 产品指标
- 记账完成率 > 80%（一次记账成功率）
- AI 分类准确率 > 85%
- 截图记账使用率 > 40%
- 文本粘贴记账使用率 > 30%
- 语音记账使用率 > 20%
- 移动端用户占比 > 60%
- 家庭用户占比 > 30%（使用家庭功能的用户）
- 用户月留存率 > 30%
- 平均日活跃时间 > 2 分钟
- 家庭成员平均活跃数 > 2 人/家庭

---

## 15. 总结

Money 是一款定位清晰的个人/家庭记账工具，通过分阶段实现，从基础记账到 AI 智能化，逐步完善功能。技术栈成熟可靠，部署简单，适合个人或小团队快速开发和迭代。

**核心特性**：
- **Apple Design 风格**：极致简洁，流畅动画，圆润设计，暗黑模式支持
- **软删除功能**：所有删除操作可恢复，便于查账核对，30 天自动清理
- **移动优先设计**：响应式适配全设备，iOS 原生体验
- 支持支付宝/微信账单快速导入，保留文件原件
- 截图自动识别，3秒完成记账
- 文本粘贴智能录入（短信、聊天记录等）
- ASR 语音识别录入（多语言支持）
- **手动录入优化**：3 步完成记账，智能联想，快捷键支持
- 自定义标签功能（时间段标签、颜色图标）
- AI 智能分类和建议
- 丰富的数据可视化洞察（含桑基图资金流向）
- 家庭多用户支持，数据合并展示和分析
- 看板截图分享功能（前端 html2canvas + 可选 Playwright）
- 管理员可配置多个 AI 模型（15+ 种服务提供商）
- 灵活的基础设施配置（SQLite/MySQL/PostgreSQL、Redis、MinIO）
- 回收站管理（查看、恢复、批量操作）
- 极简设计，零学习成本

**核心场景**：
- **个人记账**：快速记录日常收支，AI 辅助分类，4 种录入方式（手动、截图、语音、文本）
- **家庭财务**：夫妻/家庭成员共同记账，合并查看家庭总览
- **数据导入**：一键导入支付宝/微信账单，文件原件保留
- **智能分析**：桑基图展示资金流向，看板截图分享
- **多模态输入**：手动表单（3步完成）、截图 OCR、语音识别、文本粘贴，灵活选择
- **查账核对**：软删除支持，回收站管理，所有删除可恢复

**UI/UX 亮点**：
- **Apple Design**：遵循 Human Interface Guidelines，极致简洁美观
- **流畅动画**：所有过渡动画 300ms，自然流畅
- **暗黑模式**：完美支持系统暗黑模式
- **触控优化**：44px 最小点击区域，左滑操作，长按菜单
- **大字体**：金额输入大字体展示，清晰易读
- **智能联想**：基于历史记录推荐分类和备注
- **快捷键**：Ctrl+Enter 提交，Esc 取消，Tab 切换

**AI 能力**：
- 支持 15+ 种主流 AI 服务提供商（OpenAI/DeepSeek/Gemini/Anthropic/Qwen/Zhipu/Ollama 等）
- 支持 8+ 种 ASR 服务提供商（OpenAI Whisper/Google/Azure/阿里云/腾讯云等）
- 统一 OpenAI 兼容接口，易于扩展
- 智能分类、消费建议、异常检测、支出预测
- OCR 图像识别、ASR 语音识别、文本解析三大 AI 输入方式

**数据安全**：
- 软删除设计，所有删除操作可恢复
- 30 天自动清理过期项目（可配置）
- 文件原件保留，可随时查看和下载
- 支持导出备份，多设备同步

核心理念：**Apple Design + 极简设计 + AI 智能 + 数据驱动 + 移动优先 + 家庭协作 + 多模态输入 + 软删除安全 = 更好的理财体验**。

---

**文档版本**: v2.0
**最后更新**: 2026-03-14

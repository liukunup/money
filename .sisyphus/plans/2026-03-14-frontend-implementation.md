# Money Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标**: 实现 Money 前端应用（Vue 3 + TypeScript），遵循 Apple Design 风格，提供完整的收支管理、分类管理和用户认证功能。

**技术栈**:
- Vue 3.5 + TypeScript 5.8
- Vite 6 + Vitest
- Pinia 3 + Vue Router 4.5
- 自定义 Apple Design 组件库
- ECharts 5（用于数据可视化）

**开发原则**:
- TDD（测试驱动开发）
- 组件优先开发
- 渐进式实现
- 每个功能独立可测试

---

## Phase 1: 项目基础设施

### Task 1.1: 项目结构初始化

**Files**:
- Create: `webui/src/assets/`
- Create: `webui/src/components/common/`
- Create: `webui/src/components/auth/`
- Create: `webui/src/components/transaction/`
- Create: `webui/src/components/category/`
- Create: `webui/src/components/ui/`
- Create: `webui/src/composables/`
- Create: `webui/src/stores/`
- Create: `webui/src/router/`
- Create: `webui/src/services/`
- Create: `webui/src/types/`
- Create: `webui/src/utils/`
- Create: `webui/src/views/`
- Create: `webui/public/`

**Step 1: 创建目录结构**

```bash
cd /Users/liukunup/Documents/repo/money/webui
mkdir -p src/{assets,components/{common,auth,transaction,category,ui},composables,stores,router,services,types,utils,views}
mkdir -p public
mkdir -p tests/{unit,e2e}
```

**Step 2: 更新 package.json 依赖**

```json
{
  "dependencies": {
    "pinia": "^3.0.1",
    "vue": "^3.5.13",
    "vue-router": "^4.5.0",
    "axios": "^1.6.0",
    "echarts": "^5.5.0",
    "date-fns": "^3.0.0"
  }
}
```

**Step 3: 安装依赖**

```bash
cd /Users/liukunup/Documents/repo/money/webui
npm install
```

Expected: All dependencies installed successfully

**Step 4: 提交项目结构**

```bash
git add webui/src/ webui/public/ webui/package.json
git commit -m "feat(frontend): initialize frontend project structure"
```

---

### Task 1.2: 类型定义

**Files**:
- Create: `webui/src/types/index.ts`
- Create: `webui/src/types/api.ts`
- Create: `webui/src/types/models.ts`

**Step 1: 编写类型定义测试**

```typescript
// tests/unit/types.test.ts
import { describe, it, expect } from 'vitest';
import type { User, Category, Transaction } from '@/types';

describe('Type Definitions', () => {
  it('should have correct User type structure', () => {
    const user: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      display_name: 'Test User',
      is_active: true,
      created_at: new Date().toISOString()
    };
    expect(user.id).toBe(1);
  });

  it('should have correct Transaction type structure', () => {
    const transaction: Transaction = {
      id: 1,
      amount: '45.50',
      type: 'expense',
      category_id: 1,
      date: '2026-03-14',
      note: 'Test transaction',
      created_at: new Date().toISOString()
    };
    expect(transaction.type).toBe('expense');
  });
});
```

**Step 2: 运行类型测试（预期失败）**

```bash
cd /Users/liukunup/Documents/repo/money/webui
npm run test:unit tests/unit/types.test.ts
```

Expected: FAIL with "Cannot find module '@/types'"

**Step 3: 实现类型定义**

```typescript
// webui/src/types/models.ts
export interface User {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  type: 'income' | 'expense';
  icon?: string;
  created_at: string;
}

export interface Transaction {
  id: number;
  amount: string;
  type: 'income' | 'expense';
  category_id: number;
  date: string;
  note?: string;
  created_at: string;
}

export interface TransactionFilters {
  type?: 'income' | 'expense';
  category_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
}
```

```typescript
// webui/src/types/api.ts
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}
```

```typescript
// webui/src/types/index.ts
export * from './models';
export * from './api';
```

**Step 4: 运行类型测试**

```bash
npm run test:unit tests/unit/types.test.ts
```

Expected: PASS

**Step 5: 提交类型定义**

```bash
git add webui/src/types/ tests/unit/types.test.ts
git commit -m "feat(frontend): add TypeScript type definitions"
```

---

### Task 1.3: API 服务层

**Files**:
- Create: `webui/src/services/api.ts`
- Create: `webui/src/services/auth.service.ts`
- Create: `webui/src/services/transactions.service.ts`
- Create: `webui/src/services/categories.service.ts`

**Step 1: 编写 API 服务测试**

```typescript
// tests/unit/services/auth.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from '@/services/auth.service';
import axios from 'axios';

vi.mock('axios');

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call login API correctly', async () => {
    const mockResponse = { data: { access_token: 'test-token', token_type: 'bearer' } };
    vi.mocked(axios.post).mockResolvedValue(mockResponse);

    const result = await authService.login('testuser', 'password123');
    expect(result.access_token).toBe('test-token');
  });
});
```

**Step 2: 运行 API 服务测试（预期失败）**

```bash
npm run test:unit tests/unit/services/auth.service.test.ts
```

Expected: FAIL with "Cannot find module '@/services/auth.service'"

**Step 3: 实现 API 服务**

```typescript
// webui/src/services/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

```typescript
// webui/src/services/auth.service.ts
import apiClient from './api';
import type { LoginCredentials, RegisterData, LoginResponse, User } from '@/types';

export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post<LoginResponse>('/users/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/users/register', data);
    return response.data;
  },

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  setToken(token: string) {
    localStorage.setItem('auth_token', token);
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};
```

```typescript
// webui/src/services/transactions.service.ts
import apiClient from './api';
import type { Transaction, TransactionCreate, TransactionUpdate, TransactionFilters } from '@/types';

export const transactionsService = {
  async getAll(filters?: TransactionFilters): Promise<Transaction[]> {
    const response = await apiClient.get<Transaction[]>('/transactions/', { params: filters });
    return response.data;
  },

  async getById(id: number): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  async create(data: TransactionCreate): Promise<Transaction> {
    const response = await apiClient.post<Transaction>('/transactions/', data);
    return response.data;
  },

  async update(id: number, data: TransactionUpdate): Promise<Transaction> {
    const response = await apiClient.put<Transaction>(`/transactions/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/transactions/${id}`);
  },
};
```

```typescript
// webui/src/services/categories.service.ts
import apiClient from './api';
import type { Category, CategoryCreate } from '@/types';

export const categoriesService = {
  async getAll(type?: 'income' | 'expense'): Promise<Category[]> {
    const response = await apiClient.get<Category[]>('/categories/', {
      params: type ? { type } : undefined,
    });
    return response.data;
  },

  async getById(id: number): Promise<Category> {
    const response = await apiClient.get<Category>(`/categories/${id}`);
    return response.data;
  },

  async create(data: CategoryCreate): Promise<Category> {
    const response = await apiClient.post<Category>('/categories/', data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/categories/${id}`);
  },
};
```

**Step 4: 运行 API 服务测试**

```bash
npm run test:unit tests/unit/services/auth.service.test.ts
npm run test:unit tests/unit/services/transactions.service.test.ts
npm run test:unit tests/unit/services/categories.service.test.ts
```

Expected: PASS

**Step 5: 提交 API 服务**

```bash
git add webui/src/services/ tests/unit/services/
git commit -m "feat(frontend): implement API service layer"
```

---

### Task 1.4: Pinia Store 层

**Files**:
- Create: `webui/src/stores/auth.ts`
- Create: `webui/src/stores/transactions.ts`
- Create: `webui/src/stores/categories.ts`
- Create: `webui/src/stores/ui.ts`

**Step 1: 编写 Store 测试**

```typescript
// tests/unit/stores/auth.test.ts
import { describe, it, expect, beforeEach, setActivePinia } from 'vitest';
import { createPinia } from 'pinia';
import { useAuthStore } from '@/stores/auth';

describe('AuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should initialize with no user', () => {
    const store = useAuthStore();
    expect(store.user).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });
});
```

**Step 2: 运行 Store 测试（预期失败）**

```bash
npm run test:unit tests/unit/stores/auth.test.ts
```

Expected: FAIL with "Cannot find module '@/stores/auth'"

**Step 3: 实现 Store**

```typescript
// webui/src/stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types';
import { authService } from '@/services/auth.service';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(authService.getToken());

  // Getters
  const isAuthenticated = computed(() => !!token.value);

  // Actions
  async function login(username: string, password: string) {
    const response = await authService.login(username, password);
    token.value = response.access_token;
    authService.setToken(response.access_token);
  }

  async function register(data: { username: string; email: string; password: string }) {
    const newUser = await authService.register(data);
    user.value = newUser;
  }

  function logout() {
    user.value = null;
    token.value = null;
    authService.logout();
  }

  function checkAuth() {
    const storedToken = authService.getToken();
    if (storedToken) {
      token.value = storedToken;
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
  };
});
```

```typescript
// webui/src/stores/transactions.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Transaction, TransactionCreate, TransactionUpdate, TransactionFilters } from '@/types';
import { transactionsService } from '@/services/transactions.service';

export const useTransactionsStore = defineStore('transactions', () => {
  // State
  const transactions = ref<Transaction[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const filters = ref<TransactionFilters>({});

  // Actions
  async function fetchTransactions(fetchFilters?: TransactionFilters) {
    loading.value = true;
    error.value = null;
    try {
      const data = await transactionsService.getAll(fetchFilters || filters.value);
      transactions.value = data;
      if (fetchFilters) {
        filters.value = fetchFilters;
      }
    } catch (err) {
      error.value = 'Failed to fetch transactions';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTransaction(data: TransactionCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newTransaction = await transactionsService.create(data);
      transactions.value.unshift(newTransaction);
      return newTransaction;
    } catch (err) {
      error.value = 'Failed to create transaction';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTransaction(id: number, data: TransactionUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await transactionsService.update(id, data);
      const index = transactions.value.findIndex(t => t.id === id);
      if (index !== -1) {
        transactions.value[index] = updated;
      }
      return updated;
    } catch (err) {
      error.value = 'Failed to update transaction';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTransaction(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await transactionsService.delete(id);
      transactions.value = transactions.value.filter(t => t.id !== id);
    } catch (err) {
      error.value = 'Failed to delete transaction';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function setFilters(newFilters: TransactionFilters) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function clearFilters() {
    filters.value = {};
  }

  return {
    transactions,
    loading,
    error,
    filters,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    setFilters,
    clearFilters,
  };
});
```

```typescript
// webui/src/stores/categories.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Category, CategoryCreate } from '@/types';
import { categoriesService } from '@/services/categories.service';

export const useCategoriesStore = defineStore('categories', () => {
  // State
  const categories = ref<Category[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense'));
  const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income'));

  // Actions
  async function fetchCategories(type?: 'income' | 'expense') {
    loading.value = true;
    error.value = null;
    try {
      const data = await categoriesService.getAll(type);
      categories.value = data;
    } catch (err) {
      error.value = 'Failed to fetch categories';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createCategory(data: CategoryCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newCategory = await categoriesService.create(data);
      categories.value.push(newCategory);
      return newCategory;
    } catch (err) {
      error.value = 'Failed to create category';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteCategory(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await categoriesService.delete(id);
      categories.value = categories.value.filter(c => c.id !== id);
    } catch (err) {
      error.value = 'Failed to delete category';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    categories,
    loading,
    error,
    expenseCategories,
    incomeCategories,
    fetchCategories,
    createCategory,
    deleteCategory,
  };
});
```

```typescript
// webui/src/stores/ui.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export const useUIStore = defineStore('ui', () => {
  // State
  const theme = ref<'light' | 'dark' | 'auto'>('auto');
  const sidebarCollapsed = ref(false);
  const modalOpen = ref(false);
  const toastMessages = ref<ToastMessage[]>([]);

  // Actions
  function setTheme(newTheme: 'light' | 'dark' | 'auto') {
    theme.value = newTheme;
    if (newTheme !== 'auto') {
      localStorage.setItem('theme', newTheme);
    }
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  function openModal() {
    modalOpen.value = true;
  }

  function closeModal() {
    modalOpen.value = false;
  }

  function showToast(message: ToastMessage) {
    toastMessages.value.push(message);
    if (message.duration) {
      setTimeout(() => {
        dismissToast(message.id);
      }, message.duration);
    }
  }

  function dismissToast(id: string) {
    toastMessages.value = toastMessages.value.filter(t => t.id !== id);
  }

  return {
    theme,
    sidebarCollapsed,
    modalOpen,
    toastMessages,
    setTheme,
    toggleSidebar,
    openModal,
    closeModal,
    showToast,
    dismissToast,
  };
});
```

**Step 4: 运行 Store 测试**

```bash
npm run test:unit tests/unit/stores/
```

Expected: PASS

**Step 5: 提交 Store**

```bash
git add webui/src/stores/ tests/unit/stores/
git commit -m "feat(frontend): implement Pinia stores for state management"
```

---

## Phase 2: Apple Design 组件库

### Task 2.1: 基础组件 - Button

**Files**:
- Create: `webui/src/components/ui/Button.vue`
- Create: `tests/unit/components/Button.test.ts`

**Step 1: 编写 Button 组件测试**

```typescript
// tests/unit/components/Button.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from '@/components/ui/Button.vue';

describe('Button', () => {
  it('should render with correct text', () => {
    const wrapper = mount(Button, {
      props: { text: 'Click me' },
    });
    expect(wrapper.text()).toContain('Click me');
  });

  it('should emit click event', async () => {
    const wrapper = mount(Button, {
      props: { text: 'Click me' },
    });
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted()).toHaveProperty('click');
  });
});
```

**Step 2: 运行 Button 测试（预期失败）**

```bash
npm run test:unit tests/unit/components/Button.test.ts
```

Expected: FAIL with "Cannot find module '@/components/ui/Button.vue'"

**Step 3: 实现 Button 组件**

```vue
<!-- webui/src/components/ui/Button.vue -->
<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  text?: string;
  variant?: 'primary' | 'secondary' | 'destructive' | 'success';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  variant: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  type: 'button',
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const buttonClasses = computed(() => {
  const classes = ['btn'];

  // Variant classes
  classes.push(`btn--${props.variant}`);

  // Size classes
  classes.push(`btn--${props.size}`);

  // State classes
  if (props.disabled || props.loading) {
    classes.push('btn--disabled');
  }

  return classes.join(' ');
});

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>

<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="btn__spinner"></span>
    <span v-else>{{ text }}</span>
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-family);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-default);
  white-space: nowrap;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn--primary:hover {
  background: var(--color-primary-dark);
}

.btn--secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.btn--secondary:hover {
  background: var(--color-bg-tertiary);
}

.btn--destructive {
  background: var(--color-error);
  color: var(--color-text-inverse);
}

.btn--destructive:hover {
  filter: brightness(0.9);
}

.btn--success {
  background: var(--color-success);
  color: var(--color-text-inverse);
}

.btn--small {
  height: 36px;
  padding: 0 var(--space-3);
  font-size: var(--font-size-sm);
}

.btn--medium {
  height: 44px;
  padding: 0 var(--space-4);
  font-size: var(--font-size-base);
}

.btn--large {
  height: 52px;
  padding: 0 var(--space-6);
  font-size: var(--font-size-lg);
}

.btn--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn__spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
```

**Step 4: 运行 Button 测试**

```bash
npm run test:unit tests/unit/components/Button.test.ts
```

Expected: PASS

**Step 5: 提交 Button 组件**

```bash
git add webui/src/components/ui/Button.vue tests/unit/components/Button.test.ts
git commit -m "feat(frontend): add Apple Design Button component"
```

### Task 2.2: Input 组件

**Files**:
- Create: `webui/src/components/ui/Input.vue`
- Create: `tests/unit/components/Input.test.ts`

**Step 1-5**: 同 Button 组件流程（测试失败 → 实现 → 测试通过）

**实现概要**:
- Floating label（iOS 风格）
- 错误状态显示
- 密码显示/隐藏切换
- 前缀/后缀图标支持

---

### Task 2.3: Card 组件

**Files**:
- Create: `webui/src/components/ui/Card.vue`
- Create: `tests/unit/components/Card.test.ts`

**Step 1-5**: 同 Button 组件流程

**实现概要**:
- 白色背景，微妙阴影
- 圆角 12-16px
- Hover 浮起效果
- 可选填充选项

---

### Task 2.4: Modal 组件

**Files**:
- Create: `webui/src/components/ui/Modal.vue`
- Create: `tests/unit/components/Modal.test.ts`

**Step 1-5**: 同 Button 组件流程

**实现概要**:
- 居中模态框
- 背景模糊遮罩
- 平滑滑入动画
- ESC 键关闭
- 点击遮罩关闭

---

### Task 2.5: List 组件

**Files**:
- Create: `webui/src/components/ui/List.vue`
- Create: `webui/src/components/ui/ListItem.vue`
- Create: `tests/unit/components/List.test.ts`

**Step 1-5**: 同 Button 组件流程

**实现概要**:
- 分组显示
- 分隔线（可选）
- iOS 风格左滑操作
- 下拉刷新
- 无限滚动

---

## Phase 3: 认证功能

### Task 3.1: Login View

**Files**:
- Create: `webui/src/views/LoginView.vue`
- Create: `tests/e2e/login.spec.ts`

**Step 1: 编写 Login View 测试**

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('should login successfully', async ({ page }) => {
  await page.goto('http://localhost:5173/login');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('http://localhost:5173/');
});
```

**Step 2**: 实现 LoginView（使用之前创建的 UI 组件）

**Step 3**: 提交 Login View

```bash
git add webui/src/views/LoginView.vue tests/e2e/login.spec.ts
git commit -m "feat(frontend): implement login view with Apple Design"
```

### Task 3.2: Register View

**Files**:
- Create: `webui/src/views/RegisterView.vue`
- Create: `tests/e2e/register.spec.ts`

**Step 1-3**: 同 Login View 流程

---

## Phase 4: 核心功能

### Task 4.1: Dashboard View

**Files**:
- Create: `webui/src/views/DashboardView.vue`
- Create: `webui/src/components/DashboardSummaryCard.vue`

**实现内容**:
- 总览卡片（余额、收入、支出）
- 最近交易列表
- 快速添加按钮（FAB）

### Task 4.2: Transactions View

**Files**:
- Create: `webui/src/views/TransactionListView.vue`
- Create: `webui/src/components/TransactionFormModal.vue`

**实现内容**:
- 交易列表（按日期分组）
- 筛选器（类型、分类、日期）
- 交易表单模态框
- 添加/编辑/删除交易

### Task 4.3: Categories View

**Files**:
- Create: `webui/src/views/CategoryListView.vue`
- Create: `webui/src/components/CategoryFormModal.vue`

**实现内容**:
- 分类网格展示
- 收入/支出分类标签页
- 添加/编辑/删除分类

---

## Phase 5: 路由和导航

### Task 5.1: Router 配置

**Files**:
- Create: `webui/src/router/index.ts`

**实现内容**:
- 路由定义
- 认证守卫
- 重定向逻辑

### Task 5.2: App.vue 和布局

**Files**:
- Modify: `webui/src/App.vue`

**实现内容**:
- 主布局结构
- 头部导航
- 侧边栏（桌面端）
- 主题切换

---

## Phase 6: Apple Design 系统集成

### Task 6.1: CSS 变量系统

**Files**:
- Create: `webui/src/styles/variables.css`
- Create: `webui/src/styles/reset.css`

**实现内容**:
- 色彩系统（主色、中性色、语义色）
- 字体系统（大小、字重、行高）
- 间距系统（space tokens）
- 圆角系统
- 阴影系统
- 动画系统

### Task 6.2: 暗黑模式

**实现内容**:
- CSS 媒体查询
- Store 集成
- localStorage 持久化

---

## 验证步骤

每个 Phase 完成后：

1. **运行单元测试**:
   ```bash
   npm run test:unit
   ```

2. **运行 E2E 测试**:
   ```bash
   npm run build
   npm run test:e2e
   ```

3. **TypeScript 类型检查**:
   ```bash
   npm run type-check
   ```

4. **Lint 检查**:
   ```bash
   npm run lint
   ```

5. **本地开发测试**:
   ```bash
   npm run dev
   ```
   在浏览器中手动测试所有功能

---

## 提交规范

每个 Task 完成后提交：

```bash
git add .
git commit -m "feat(frontend): [brief description]"
```

---

## 总结

本实施计划涵盖：
- ✅ 项目基础设施（类型、API 服务、Store）
- ✅ Apple Design 组件库（Button、Input、Card、Modal、List）
- ✅ 认证功能（Login、Register）
- ✅ 核心功能（Dashboard、Transactions、Categories）
- ✅ 路由和导航
- ✅ Apple Design 系统集成（CSS 变量、暗黑模式）

**下一步**: 按照此计划逐步实现每个任务，确保每个步骤都有测试覆盖。

---

**文档版本**: v1.0
**创建日期**: 2026-03-14
**作者**: Sisyphus

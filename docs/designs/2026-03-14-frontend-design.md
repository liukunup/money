# Money Frontend Design Document

**Created**: 2026-03-14
**Version**: 1.0
**Author**: Sisyphus

## Overview

This document outlines the design and architecture for the Money frontend application (Vue 3 + TypeScript), following Apple Design guidelines for a polished, intuitive user experience.

## Design Philosophy

**Apple Design Principles Applied:**
1. **Clarity**: Clean interface, clear hierarchy, intuitive navigation
2. **Deference**: Content takes priority, UI elements stay in the background
3. **Depth**: Subtle shadows, transitions, and animations for spatial relationships
4. **Consistency**: Unified visual language across all components
5. **Feedback**: Immediate visual feedback for all user interactions

---

## 1. Technology Stack

### Core Framework
- **Vue 3.5** - Composition API with `<script setup>` syntax
- **TypeScript 5.8** - Full type safety across application
- **Vite 6** - Fast HMR, optimized production builds

### State Management
- **Pinia 3** - Modern, type-safe state management
- Stores: `auth`, `transactions`, `categories`, `ui`

### Routing
- **Vue Router 4.5** - SPA navigation with history mode
- Route guards: authentication, data loading

### UI Libraries
- **Custom components** - Apple Design style (no external UI framework)
- **ECharts 5** - Data visualization (for Phase 2)
- **Tailwind CSS** (optional) - Utility classes for rapid styling
- **CSS Variables** - Theme system for light/dark mode support

### Development Tools
- **Vitest** - Unit testing
- **Playwright** - E2E testing
- **ESLint + Prettier** - Code quality and formatting

---

## 2. Architecture

### Folder Structure

```
webui/
├── src/
│   ├── assets/           # Static assets (images, icons)
│   ├── components/        # Reusable Vue components
│   │   ├── common/      # Shared components (Button, Input, Card)
│   │   ├── auth/        # Authentication components
│   │   ├── transaction/  # Transaction-related components
│   │   ├── category/    # Category-related components
│   │   └── ui/          # Apple Design UI components
│   ├── composables/      # Vue composables (useApi, useLocalStorage)
│   ├── stores/          # Pinia stores
│   ├── router/          # Vue Router configuration
│   ├── services/         # API service layer
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── views/           # Page-level components
│   ├── App.vue          # Root component
│   └── main.ts         # Application entry point
├── public/              # Static files
├── tests/               # Test files
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json
```

### Component Hierarchy

```
App.vue
├── Layout/
│   ├── Header.vue (navigation, user menu)
│   ├── MainContent.vue
│   └── Sidebar.vue (desktop only)
├── Auth/
│   ├── LoginView.vue
│   └── RegisterView.vue
├── Dashboard/
│   ├── DashboardView.vue
│   └── QuickAddButton.vue (FAB)
├── Transactions/
│   ├── TransactionListView.vue
│   ├── TransactionFormModal.vue
│   └── TransactionItem.vue
├── Categories/
│   ├── CategoryListView.vue
│   └── CategoryFormModal.vue
└── Settings/
    └── SettingsView.vue
```

---

## 3. Apple Design System

### 3.1 Color System

```css
:root {
  /* Primary Colors */
  --color-primary: #007AFF;
  --color-primary-light: #5AC8FA;
  --color-primary-dark: #0051D5;

  /* Neutral Colors */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F2F2F7;
  --color-bg-tertiary: #E5E5EA;
  --color-bg-elevated: #FFFFFF;

  /* Text Colors */
  --color-text-primary: #000000;
  --color-text-secondary: #8E8E93;
  --color-text-tertiary: #C7C7CC;
  --color-text-inverse: #FFFFFF;

  /* Semantic Colors */
  --color-success: #34C759;
  --color-warning: #FF9500;
  --color-error: #FF3B30;
  --color-info: #5AC8FA;
  --color-income: #34C759;
  --color-expense: #FF3B30;

  /* Separator */
  --color-separator: rgba(60, 60, 67, 0.36);
  --color-separator-opaque: #C6C6C8;
}
```

### 3.2 Typography

```css
:root {
  --font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 11px;
  --font-size-sm: 13px;
  --font-size-base: 17px;
  --font-size-lg: 20px;
  --font-size-xl: 24px;
  --font-size-2xl: 28px;
  --font-size-3xl: 34px;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  --letter-spacing-tight: -0.02em;
  --letter-spacing-normal: 0em;
  --letter-spacing-wide: 0.02em;
}
```

### 3.3 Spacing System

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

### 3.4 Border Radius

```css
:root {
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 28px;
  --radius-full: 9999px;
}
```

### 3.5 Shadows

```css
:root {
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.15);
  --shadow-xl: 0 12px 32px rgba(0, 0, 0, 0.18);
}
```

### 3.6 Animation System

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;

  --ease-default: cubic-bezier(0.4, 0.0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-spring: cubic-bezier(0.25, 0.1, 0.25, 1.0);
  --ease-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 4. Core Components

### 4.1 Button Component

**Variants:**
- Primary (filled blue)
- Secondary (gray)
- Tertiary (transparent with text)
- Destructive (red)
- Success (green)

**Sizes:**
- Small (36px height)
- Medium (44px height) - default
- Large (52px height)

**States:**
- Default
- Hover
- Active (pressed)
- Disabled
- Loading

**Usage:**
```vue
<Button variant="primary" size="medium" @click="handleSubmit">
  Save Transaction
</Button>
```

### 4.2 Input Component

**Features:**
- Floating label (iOS style)
- Error validation display
- Clear button
- Helper text
- Prefix/suffix icons

**States:**
- Default
- Focused
- Error
- Disabled

### 4.3 Card Component

**Features:**
- White background with subtle shadow
- Rounded corners (12-16px)
- Hover elevation effect
- Padding options

### 4.4 Modal/Sheet Component

**Types:**
- **Center Modal**: For dialogs, forms
- **Bottom Sheet**: For mobile-first actions

**Features:**
- Backdrop blur
- Swipe-to-dismiss (bottom sheet)
- Smooth slide-in animation
- Keyboard dismissal

### 4.5 List Component

**Features:**
- Grouped sections
- Separators (optional)
- Swipe actions (mobile)
- Pull-to-refresh
- Infinite scroll support

**Item Structure:**
```vue
<List>
  <ListGroup title="Today">
    <ListItem
      :title="transaction.note"
      :subtitle="transaction.category.name"
      :leading="{ icon: transaction.category.icon }"
      :trailing="`¥${transaction.amount}`"
      @swipe="handleDelete"
    />
  </ListGroup>
</List>
```

---

## 5. Views & Pages

### 5.1 Authentication Views

#### Login View
**Layout:**
- Centered card on desktop
- Full-screen on mobile

**Components:**
- Logo/branding
- Username input
- Password input (with show/hide toggle)
- Login button
- "Forgot password" link
- "Create account" link

#### Register View
**Layout:**
- Centered card

**Components:**
- Logo/branding
- Username input
- Email input
- Password input
- Confirm password input
- Register button
- "Already have an account" link

### 5.2 Dashboard View

**Layout:**
- Header with navigation
- Main content area with cards

**Components:**
- **Summary Cards:**
  - Total balance
  - Total income (this month)
  - Total expense (this month)
  - Transaction count

- **Quick Actions:**
  - Add transaction FAB (floating action button)
  - Quick category selector

- **Recent Transactions:**
  - Last 10 transactions
  - "View all" link

### 5.3 Transactions View

**Layout:**
- Header with date filter
- List of transaction groups by date
- FAB for quick add

**Features:**
- Date range selector
- Category filter
- Type filter (income/expense)
- Search by note
- Swipe to delete (mobile)
- Pull-to-refresh
- Infinite scroll

### 5.4 Transaction Form Modal

**Fields:**
- Type toggle (income/expense) - segmented control
- Amount input (large, prominent)
- Category selector (searchable dropdown)
- Date picker
- Time picker
- Note textarea (optional)

**Validation:**
- Amount > 0
- Category required
- Date required

**Actions:**
- Save
- Cancel
- Save as draft (localStorage)

### 5.5 Categories View

**Layout:**
- Grid of category cards
- Tabs for income/expense

**Features:**
- Add category button
- Edit category (long press or swipe)
- Delete category (with confirmation)
- Category icon selector

---

## 6. State Management (Pinia)

### 6.1 Auth Store

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

interface AuthActions {
  login(credentials: LoginCredentials): Promise<void>;
  register(data: RegisterData): Promise<void>;
  logout(): void;
  checkAuth(): void;
}
```

### 6.2 Transactions Store

```typescript
interface TransactionsState {
  transactions: Transaction[];
  loading: boolean;
  error: string | null;
  filters: TransactionFilters;
}

interface TransactionsActions {
  fetchTransactions(filters?: TransactionFilters): Promise<void>;
  createTransaction(data: TransactionCreate): Promise<void>;
  updateTransaction(id: number, data: TransactionUpdate): Promise<void>;
  deleteTransaction(id: number): Promise<void>;
  setFilters(filters: TransactionFilters): void;
  clearFilters(): void;
}
```

### 6.3 Categories Store

```typescript
interface CategoriesState {
  categories: Category[];
  loading: boolean;
  error: string | null;
}

interface CategoriesActions {
  fetchCategories(type?: 'income' | 'expense'): Promise<void>;
  createCategory(data: CategoryCreate): Promise<void>;
  deleteCategory(id: number): Promise<void>;
}
```

### 6.4 UI Store

```typescript
interface UIState {
  theme: 'light' | 'dark' | 'auto';
  sidebarCollapsed: boolean;
  modalOpen: boolean;
  toastMessages: ToastMessage[];
}

interface UIActions {
  setTheme(theme: 'light' | 'dark' | 'auto'): void;
  toggleSidebar(): void;
  showToast(message: ToastMessage): void;
  dismissToast(id: string): void;
}
```

---

## 7. API Service Layer

### 7.1 Base API Client

```typescript
// services/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
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
      // Token expired, logout user
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 7.2 Service Modules

```typescript
// services/auth.service.ts
export const authService = {
  async login(username: string, password: string) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await apiClient.post<LoginResponse>('/users/login', formData);
    return response.data;
  },

  async register(data: RegisterData) {
    const response = await apiClient.post<User>('/users/register', data);
    return response.data;
  },
};

// services/transactions.service.ts
export const transactionsService = {
  async getAll(filters?: TransactionFilters) {
    const response = await apiClient.get<Transaction[]>('/transactions/', { params: filters });
    return response.data;
  },

  async getById(id: number) {
    const response = await apiClient.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  async create(data: TransactionCreate) {
    const response = await apiClient.post<Transaction>('/transactions/', data);
    return response.data;
  },

  async update(id: number, data: TransactionUpdate) {
    const response = await apiClient.put<Transaction>(`/transactions/${id}`, data);
    return response.data;
  },

  async delete(id: number) {
    await apiClient.delete(`/transactions/${id}`);
  },
};

// services/categories.service.ts
export const categoriesService = {
  async getAll(type?: 'income' | 'expense') {
    const response = await apiClient.get<Category[]>('/categories/', {
      params: type ? { type } : undefined
    });
    return response.data;
  },

  async create(data: CategoryCreate) {
    const response = await apiClient.post<Category>('/categories/', data);
    return response.data;
  },

  async delete(id: number) {
    await apiClient.delete(`/categories/${id}`);
  },
};
```

---

## 8. Routing Structure

```typescript
// router/index.ts
const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/transactions',
    name: 'transactions',
    component: TransactionListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'categories',
    component: CategoryListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false }
  }
];
```

### Route Guards

```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else if (to.meta.requiresAuth === false && isAuthenticated) {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});
```

---

## 9. Composables

### 9.1 useLocalStorage

```typescript
export function useLocalStorage<T>(key: string, initialValue: T) {
  const storedValue = localStorage.getItem(key);
  const state = ref<T>(storedValue ? JSON.parse(storedValue) : initialValue);

  watch(state, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue));
  }, { deep: true });

  return state;
}
```

### 9.2 useToast

```typescript
export function useToast() {
  const uiStore = useUIStore();

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    uiStore.showToast({
      id: Date.now().toString(),
      message,
      type,
      duration: 3000
    });
  };

  return { showToast };
}
```

---

## 10. Responsive Design

### Breakpoints

```css
:root {
  --breakpoint-xs: 375px;   /* Small phones */
  --breakpoint-sm: 640px;   /* Large phones */
  --breakpoint-md: 768px;   /* Tablets */
  --breakpoint-lg: 1024px;  /* Small desktops */
  --breakpoint-xl: 1280px;  /* Desktops */
  --breakpoint-2xl: 1536px; /* Large desktops */
}
```

### Mobile Optimizations

- Touch-friendly tap targets (44x44px minimum)
- Swipe gestures for list actions
- Bottom sheet modals
- Pull-to-refresh
- FAB (floating action button) for quick actions
- Keyboard avoidance on inputs

### Desktop Optimizations

- Sidebar navigation
- Hover states
- Keyboard shortcuts
- Larger click targets
- Dense information display

---

## 11. Dark Mode Support

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #000000;
    --color-bg-secondary: #1C1C1E;
    --color-bg-tertiary: #2C2C2E;
    --color-text-primary: #FFFFFF;
    --color-text-secondary: #98989D;
    --color-text-tertiary: #636366;
    --color-separator: rgba(84, 84, 88, 0.65);
  }
}
```

Theme toggling via Pinia store with localStorage persistence.

---

## 12. Performance Considerations

### 12.1 Code Splitting

```typescript
const TransactionListView = () => import('@/views/TransactionListView.vue');
const CategoryListView = () => import('@/views/CategoryListView.vue');
```

### 12.2 Lazy Loading

- Component lazy loading
- Route-based code splitting
- Image lazy loading

### 12.3 Caching Strategy

- API response caching (in-memory, 5 min TTL)
- Category data caching (longer TTL)
- LocalStorage for offline drafts

### 12.4 Bundle Size Targets

- Initial bundle: < 200KB
- Each route chunk: < 50KB
- Total vendor chunk: < 150KB

---

## 13. Accessibility

### 13.1 ARIA Labels

All interactive elements have appropriate ARIA labels.

### 13.2 Keyboard Navigation

- Full keyboard support
- Focus indicators
- Skip to content links
- Escape key to close modals

### 13.3 Screen Reader Support

- Semantic HTML elements
- Proper heading hierarchy
- Live regions for dynamic content

---

## 14. Internationalization (i18n)

### 14.1 Default Languages

- English (en)
- Simplified Chinese (zh-CN)

### 14.2 Translation Structure

```
locales/
├── en.json
└── zh-CN.json
```

### 14.3 Date/Time Formatting

Use `Intl.DateTimeFormat` for locale-aware formatting.

---

## 15. Testing Strategy

### 15.1 Unit Tests (Vitest)

- Component rendering
- Composable behavior
- Store actions
- API service mocks

### 15.2 E2E Tests (Playwright)

- User flows (login, add transaction)
- Cross-browser testing
- Mobile viewport testing

### 15.3 Visual Regression Tests

- Screenshot comparison
- Component snapshot testing

---

## 16. Deployment

### 16.1 Environment Variables

```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Money
```

### 16.2 Build Configuration

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'echarts': ['echarts']
        }
      }
    }
  }
});
```

---

## 17. Implementation Priority

### Phase 1: Core Functionality (Week 1-2)
1. Setup project structure
2. Implement Apple Design system (colors, typography, components)
3. Authentication flows (login/register)
4. Transaction CRUD
5. Category CRUD
6. Basic dashboard with summary cards

### Phase 2: Polish & UX (Week 2-3)
7. Apple-style animations and transitions
8. Mobile optimizations (swipe gestures, FAB)
9. Dark mode support
10. Search and filtering
11. Toast notifications
12. Loading states and error handling

### Phase 3: Advanced Features (Week 3-4)
13. Data visualization (charts)
14. Budget management UI
15. Export functionality
16. Settings page
17. PWA support
18. Performance optimization

---

## 18. Success Metrics

- **Performance**: < 2s initial load, < 100ms route transitions
- **Accessibility**: WCAG 2.1 AA compliance
- **Mobile**: Lighthouse score > 90
- **Desktop**: Cross-browser compatibility (Chrome, Safari, Firefox)
- **UX**: 80%+ task completion rate for core flows

---

## Next Steps

1. **Create detailed implementation plan** breaking down components and features
2. **Setup development environment** with testing infrastructure
3. **Implement Apple Design component library** (buttons, inputs, cards, modals)
4. **Build authentication flows** with proper validation
5. **Develop transaction management** with full CRUD
6. **Create dashboard** with summary statistics
7. **Add mobile optimizations** and responsive design
8. **Implement dark mode** support
9. **Performance testing and optimization**
10. **End-to-end testing** across all flows

---

**Document Version**: 1.0
**Last Updated**: 2026-03-14

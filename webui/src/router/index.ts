import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/components/auth/LoginView.vue'
import RegisterView from '@/components/auth/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import StatisticsView from '@/views/StatisticsView.vue'
import TransactionListView from '@/views/TransactionListView.vue'
import CategoryListView from '@/views/CategoryListView.vue'
import SettingsView from '@/views/SettingsView.vue'
import BudgetListView from '@/views/BudgetListView.vue'
import AIProvidersView from '@/views/AIProvidersView.vue'
import ImportView from '@/views/ImportView.vue'
import HouseholdView from '@/views/HouseholdView.vue'
import TimePeriodListView from '@/views/TimePeriodListView.vue'
import AnomalyListView from '@/views/AnomalyListView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: StatisticsView,
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
      path: '/ai-providers',
      name: 'ai-providers',
      component: AIProvidersView,
      meta: { requiresAuth: true }
    },
    {
      path: '/import',
      name: 'import',
      component: ImportView,
      meta: { requiresAuth: true }
    },
    {
      path: '/household',
      name: 'household',
      component: HouseholdView,
      meta: { requiresAuth: true }
    },
    {
      path: '/time-periods',
      name: 'time-periods',
      component: TimePeriodListView,
      meta: { requiresAuth: true }
    },
    {
      path: '/anomalies',
      name: 'anomalies',
      component: AnomalyListView,
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
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.checkAuth()

  if (to.meta.requiresAuth !== undefined) {
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else if (!to.meta.requiresAuth && authStore.isAuthenticated) {
      next({ name: 'home' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router

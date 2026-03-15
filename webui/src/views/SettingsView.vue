<template>
  <div class="settings">
    <!-- Header -->
    <header class="settings-header">
      <h1 class="settings-title">{{ t('settings.title') }}</h1>
      <p class="settings-subtitle">{{ t('settings.subtitle') }}</p>
    </header>

    <!-- User Profile Section -->
    <section class="settings-section">
      <h2 class="section-title">{{ t('settings.profile') }}</h2>
      <Card variant="elevated" class="profile-card">
        <div class="profile-content">
          <div class="profile-avatar">
            {{ userInitial }}
          </div>
          <div class="profile-info">
            <p class="profile-name">{{ authStore.user?.display_name || authStore.user?.username || t('auth.login') }}</p>
            <p class="profile-email">{{ authStore.user?.email || t('common.noData') }}</p>
          </div>
        </div>
      </Card>
    </section>

    <!-- Language Section -->
    <section class="settings-section">
      <h2 class="section-title">{{ t('settings.language') }}</h2>
      <Card variant="elevated" class="language-card">
        <div class="language-options">
          <button
            v-for="option in languageOptions"
            :key="option.value"
            class="language-option"
            :class="{ 'language-option--active': uiStore.locale === option.value }"
            @click="uiStore.setLocale(option.value)"
          >
            <span class="language-icon">{{ option.icon }}</span>
            <span class="language-label">{{ option.label }}</span>
          </button>
        </div>
        <p class="language-desc">{{ t('settings.languageDesc') }}</p>
      </Card>
    </section>

    <!-- Theme Section -->
    <section class="settings-section">
      <h2 class="section-title">{{ t('settings.appearance') }}</h2>
      <Card variant="elevated" class="theme-card">
        <div class="theme-options">
          <button
            v-for="option in themeOptions"
            :key="option.value"
            class="theme-option"
            :class="{ 'theme-option--active': uiStore.theme === option.value }"
            @click="uiStore.setTheme(option.value)"
          >
            <span class="theme-icon">{{ option.icon }}</span>
            <span class="theme-label">{{ option.label }}</span>
          </button>
        </div>
      </Card>
    </section>

    <!-- App Info Section -->
    <section class="settings-section">
      <h2 class="section-title">{{ t('settings.about') }}</h2>
      <Card variant="elevated" class="info-card">
        <div class="info-list">
          <div class="info-item" @click="$router.push('/about')">
            <span class="info-label">{{ t('settings.aboutMoney') }}</span>
            <span class="info-value">
              v{{ appVersion }}
              <span class="info-arrow">›</span>
            </span>
          </div>
          <div class="info-divider"></div>
          <div class="info-item">
            <span class="info-label">{{ t('settings.build') }}</span>
            <span class="info-value">{{ buildNumber }}</span>
          </div>
        </div>
      </Card>
    </section>

    <!-- Logout Section -->
    <section class="settings-section">
      <Button
        variant="destructive"
        size="large"
        full-width
        @click="handleLogout"
      >
        {{ t('settings.logout') }}
      </Button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import type { LocaleType } from '@/i18n'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()
const { t } = useI18n()

// App version (would typically come from package.json or build config)
const appVersion = '1.0.0'
const buildNumber = '2026.03.15'

// Get user initial for avatar
const userInitial = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

// Language options
const languageOptions = [
  { value: 'zh-CN' as LocaleType, label: '中文', icon: '🇨🇳' },
  { value: 'en-US' as LocaleType, label: 'English', icon: '🇺🇸' },
]

// Theme options
const themeOptions = [
  { value: 'light' as const, label: t('theme.light'), icon: '☀️' },
  { value: 'dark' as const, label: t('theme.dark'), icon: '🌙' },
  { value: 'auto' as const, label: t('theme.auto'), icon: '⚙️' },
]

// Handle logout
const handleLogout = () => {
  if (confirm(t('settings.logoutConfirm'))) {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.settings {
  padding: var(--space-5);
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 100px;
}

/* Header */
.settings-header {
  margin-bottom: var(--space-8);
}

.settings-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
  letter-spacing: var(--letter-spacing-tight);
}

.settings-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Sections */
.settings-section {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--letter-spacing-wide);
  margin: 0 0 var(--space-3) var(--space-1);
}

/* Profile Card */
.profile-card {
  padding: var(--space-4);
}

.profile-content {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.profile-avatar {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: var(--color-text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.profile-email {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Language Card */
.language-card {
  padding: var(--space-2);
}

.language-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-2);
}

.language-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-2);
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.language-option:hover {
  background: var(--color-bg-secondary);
}

.language-option--active {
  background: var(--color-primary);
}

.language-option--active .language-label {
  color: var(--color-text-inverse);
}

.language-icon {
  font-size: 24px;
}

.language-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.language-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
  margin: var(--space-2) 0 0 0;
}

/* Theme Card */
.theme-card {
  padding: var(--space-2);
}

.theme-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-2);
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-2);
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.theme-option:hover {
  background: var(--color-bg-secondary);
}

.theme-option--active {
  background: var(--color-primary);
}

.theme-option--active .theme-label {
  color: var(--color-text-inverse);
}

.theme-icon {
  font-size: 24px;
}

.theme-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

/* Info Card */
.info-card {
  padding: 0;
}

.info-list {
  display: flex;
  flex-direction: column;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-default);
}

.info-item:hover {
  background: var(--color-bg-secondary);
}

.info-item:last-child {
  cursor: default;
}

.info-item:last-child:hover {
  background: transparent;
}

.info-label {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.info-value {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.info-arrow {
  font-size: var(--font-size-lg);
  color: var(--color-text-tertiary);
}

.info-divider {
  height: 1px;
  background: var(--color-separator-opaque);
  margin: 0 var(--space-4);
}

/* Responsive */
@media (max-width: 480px) {
  .settings {
    padding: var(--space-4);
  }

  .settings-title {
    font-size: var(--font-size-2xl);
  }

  .profile-avatar {
    width: 50px;
    height: 50px;
    font-size: var(--font-size-lg);
  }

  .theme-option {
    padding: var(--space-3) var(--space-1);
  }

  .theme-icon {
    font-size: 20px;
  }
}
</style>

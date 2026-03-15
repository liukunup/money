<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';
import Input from '@/components/ui/Input.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Form state
const username = ref('');
const password = ref('');
const touched = ref({
  username: false,
  password: false,
});

// Validation rules
const usernameError = computed(() => {
  if (!touched.value.username) return '';
  if (!username.value) return 'Username is required';
  if (username.value.length < 3) return 'Username must be at least 3 characters';
  return '';
});

const passwordError = computed(() => {
  if (!touched.value.password) return '';
  if (!password.value) return 'Password is required';
  if (password.value.length < 6) return 'Password must be at least 6 characters';
  return '';
});

const isFormValid = computed(() => {
  return username.value.length >= 3 && password.value.length >= 6;
});

const isLoading = computed(() => authStore.loading);
const apiError = computed(() => authStore.error);

// Handle field blur
const handleUsernameBlur = () => {
  touched.value.username = true;
};

const handlePasswordBlur = () => {
  touched.value.password = true;
};

// Handle form submission
const handleSubmit = async () => {
  // Mark all fields as touched
  touched.value.username = true;
  touched.value.password = true;

  if (!isFormValid.value) return;

  try {
    await authStore.login(username.value, password.value);
    
    // Redirect to the requested page or dashboard
    const redirectPath = route.query.redirect as string || '/';
    router.push(redirectPath);
  } catch {
    // Error is handled by the store
  }
};

// Navigate to register
const goToRegister = () => {
  router.push('/register');
};
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <!-- Logo/Header -->
        <div class="auth-header">
          <div class="auth-logo">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="1" x2="12" y2="23"></line>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <h1 class="auth-title">Welcome Back</h1>
          <p class="auth-subtitle">Sign in to continue to Money</p>
        </div>

        <!-- Error Message -->
        <div v-if="apiError" class="auth-error">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {{ apiError }}
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleSubmit" class="auth-form">
          <Input
            v-model="username"
            type="text"
            label="Username"
            placeholder="Enter your username"
            :error="usernameError"
            name="username"
            autocomplete="username"
            required
            @blur="handleUsernameBlur"
          />

          <Input
            v-model="password"
            type="password"
            label="Password"
            placeholder="Enter your password"
            :error="passwordError"
            name="password"
            autocomplete="current-password"
            required
            @blur="handlePasswordBlur"
          />

          <div class="auth-actions">
            <Button
              type="submit"
              variant="primary"
              size="large"
              :loading="isLoading"
              :disabled="!isFormValid"
              full-width
            >
              Sign In
            </Button>
          </div>
        </form>

        <!-- Links -->
        <div class="auth-links">
          <a href="#" class="auth-link auth-link--secondary">Forgot password?</a>
          <div class="auth-divider"></div>
          <button type="button" class="auth-link auth-link--primary" @click="goToRegister">
            Create an account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: var(--color-bg-secondary);
}

.auth-container {
  width: 100%;
  max-width: 360px;
}

.auth-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-lg);
  animation: slideUp 0.4s var(--ease-bounce);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header */
.auth-header {
  text-align: center;
  margin-bottom: var(--space-4);
}

.auth-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border-radius: var(--radius-lg);
  color: var(--color-text-inverse);
  margin-bottom: var(--space-3);
  animation: pulse 2s var(--ease-default) infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.auth-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.auth-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Error Message */
.auth-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 59, 48, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: var(--font-size-xs);
  margin-bottom: var(--space-4);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}

/* Form */
.auth-form {
  margin-bottom: var(--space-4);
}

.auth-actions {
  margin-top: var(--space-4);
}

/* Links */
.auth-links {
  text-align: center;
}

.auth-link {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
  transition: opacity var(--duration-fast) var(--ease-default);
}

.auth-link:hover {
  opacity: 0.8;
}

.auth-link--secondary {
  color: var(--color-text-secondary);
}

.auth-divider {
  height: 1px;
  background: var(--color-separator-opaque);
  margin: var(--space-3) 0;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .auth-page {
    padding: 0;
    align-items: flex-start;
  }

  .auth-container {
    max-width: 100%;
  }

  .auth-card {
    border-radius: 0;
    min-height: 100vh;
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .auth-logo {
    width: 40px;
    height: 40px;
  }

  .auth-title {
    font-size: var(--font-size-lg);
  }
}
</style>

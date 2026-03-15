<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button.vue';
import Input from '@/components/ui/Input.vue';

const router = useRouter();
const authStore = useAuthStore();

// Form state
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const touched = ref({
  username: false,
  email: false,
  password: false,
  confirmPassword: false,
});

// Email validation regex
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Validation rules
const usernameError = computed(() => {
  if (!touched.value.username) return '';
  if (!username.value) return 'Username is required';
  if (username.value.length < 3) return 'Username must be at least 3 characters';
  return '';
});

const emailError = computed(() => {
  if (!touched.value.email) return '';
  if (!email.value) return 'Email is required';
  if (!emailRegex.test(email.value)) return 'Please enter a valid email address';
  return '';
});

const passwordError = computed(() => {
  if (!touched.value.password) return '';
  if (!password.value) return 'Password is required';
  if (password.value.length < 6) return 'Password must be at least 6 characters';
  return '';
});

const confirmPasswordError = computed(() => {
  if (!touched.value.confirmPassword) return '';
  if (!confirmPassword.value) return 'Please confirm your password';
  if (confirmPassword.value !== password.value) return 'Passwords do not match';
  return '';
});

const isFormValid = computed(() => {
  return (
    username.value.length >= 3 &&
    emailRegex.test(email.value) &&
    password.value.length >= 6 &&
    confirmPassword.value === password.value
  );
});

const isLoading = computed(() => authStore.loading);
const apiError = computed(() => authStore.error);

// Handle field blur
const handleUsernameBlur = () => {
  touched.value.username = true;
};

const handleEmailBlur = () => {
  touched.value.email = true;
};

const handlePasswordBlur = () => {
  touched.value.password = true;
};

const handleConfirmPasswordBlur = () => {
  touched.value.confirmPassword = true;
};

// Handle form submission
const handleSubmit = async () => {
  // Mark all fields as touched
  touched.value.username = true;
  touched.value.email = true;
  touched.value.password = true;
  touched.value.confirmPassword = true;

  if (!isFormValid.value) return;

  try {
    await authStore.register({
      username: username.value,
      email: email.value,
      password: password.value,
    });
    
    // After successful registration, redirect to login
    router.push('/login?registered=true');
  } catch {
    // Error is handled by the store
  }
};

// Navigate to login
const goToLogin = () => {
  router.push('/login');
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
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <line x1="20" y1="8" x2="20" y2="14"></line>
              <line x1="23" y1="11" x2="17" y2="11"></line>
            </svg>
          </div>
          <h1 class="auth-title">Create Account</h1>
          <p class="auth-subtitle">Join Money to track your expenses</p>
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

        <!-- Register Form -->
        <form @submit.prevent="handleSubmit" class="auth-form">
          <Input
            v-model="username"
            type="text"
            label="Username"
            placeholder="Choose a username"
            :error="usernameError"
            name="username"
            autocomplete="username"
            required
            @blur="handleUsernameBlur"
          />

          <Input
            v-model="email"
            type="email"
            label="Email"
            placeholder="Enter your email"
            :error="emailError"
            name="email"
            autocomplete="email"
            required
            @blur="handleEmailBlur"
          />

          <Input
            v-model="password"
            type="password"
            label="Password"
            placeholder="Create a password"
            :error="passwordError"
            name="new-password"
            autocomplete="new-password"
            required
            @blur="handlePasswordBlur"
          />

          <Input
            v-model="confirmPassword"
            type="password"
            label="Confirm Password"
            placeholder="Confirm your password"
            :error="confirmPasswordError"
            name="confirm-password"
            autocomplete="new-password"
            required
            @blur="handleConfirmPasswordBlur"
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
              Create Account
            </Button>
          </div>
        </form>

        <!-- Links -->
        <div class="auth-links">
          <button type="button" class="auth-link" @click="goToLogin">
            Already have an account? Sign in
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
  max-width: 400px;
}

.auth-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
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
  margin-bottom: var(--space-6);
}

.auth-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, var(--color-success) 0%, var(--color-primary-light) 100%);
  border-radius: var(--radius-xl);
  color: var(--color-text-inverse);
  margin-bottom: var(--space-4);
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
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.auth-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

/* Error Message */
.auth-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(255, 59, 48, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
  animation: shake 0.5s var(--ease-default);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}

/* Form */
.auth-form {
  margin-bottom: var(--space-6);
}

.auth-actions {
  margin-top: var(--space-6);
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
    padding: var(--space-6);
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .auth-logo {
    width: 64px;
    height: 64px;
  }

  .auth-title {
    font-size: var(--font-size-xl);
  }
}
</style>

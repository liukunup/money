<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');

const handleSubmit = async () => {
  try {
    await authStore.login(username.value, password.value);
    router.push('/');
  } catch (error) {
    // Error is already handled in the store
    console.error('Login failed:', error);
  }
};
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo/Branding -->
      <div class="auth-header">
        <h1 class="auth-title">Money</h1>
        <p class="auth-subtitle">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleSubmit" class="auth-form">
        <Input
          v-model="username"
          type="text"
          label="Username"
          placeholder="Enter your username"
          :error="authStore.error"
          required
          autocomplete="username"
        />

        <Input
          v-model="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          :error="authStore.error"
          required
          autocomplete="current-password"
        />

        <Button
          type="submit"
          variant="primary"
          size="large"
          :loading="authStore.loading"
          fullWidth
        >
          {{ authStore.loading ? 'Signing in...' : 'Sign In' }}
        </Button>
      </form>

      <!-- Footer Links -->
      <div class="auth-footer">
        <router-link to="/register" class="auth-link">
          Don't have an account? Create one
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-secondary);
  padding: var(--space-4);
}

.auth-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 400px;
  padding: var(--space-8);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.auth-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
}

.auth-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.auth-footer {
  text-align: center;
  margin-top: var(--space-6);
}

.auth-link {
  font-size: var(--font-size-base);
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-default);
}

.auth-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

@media (max-width: 640px) {
  .auth-container {
    padding: var(--space-3);
  }

  .auth-card {
    padding: var(--space-6);
    max-width: none;
    border-radius: 0;
    box-shadow: none;
    background: var(--color-bg-primary);
  }
}
</style>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

const passwordMatchError = computed(() => {
  if (!password.value || !confirmPassword.value) return '';
  return password.value !== confirmPassword.value ? 'Passwords do not match' : '';
});

const handleSubmit = async () => {
  // Clear previous errors
  authStore.clearError();

  // Validate password match
  if (password.value !== confirmPassword.value) {
    return;
  }

  try {
    await authStore.register({
      username: username.value,
      email: email.value,
      password: password.value,
    });
    // Redirect to login after successful registration
    router.push('/login');
  } catch (error) {
    // Error is already handled in the store
    console.error('Registration failed:', error);
  }
};
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo/Branding -->
      <div class="auth-header">
        <h1 class="auth-title">Money</h1>
        <p class="auth-subtitle">Create your account</p>
      </div>

      <!-- Register Form -->
      <form @submit.prevent="handleSubmit" class="auth-form">
        <Input
          v-model="username"
          type="text"
          label="Username"
          placeholder="Choose a username"
          :error="authStore.error"
          required
          autocomplete="username"
          helperText="At least 3 characters"
        />

        <Input
          v-model="email"
          type="email"
          label="Email"
          placeholder="Enter your email"
          :error="authStore.error"
          required
          autocomplete="email"
        />

        <Input
          v-model="password"
          type="password"
          label="Password"
          placeholder="Create a password"
          :error="authStore.error || passwordMatchError"
          required
          autocomplete="new-password"
          helperText="At least 6 characters"
        />

        <Input
          v-model="confirmPassword"
          type="password"
          label="Confirm Password"
          placeholder="Confirm your password"
          :error="passwordMatchError"
          required
          autocomplete="new-password"
        />

        <Button
          type="submit"
          variant="primary"
          size="large"
          :loading="authStore.loading"
          :disabled="!!passwordMatchError"
          fullWidth
        >
          {{ authStore.loading ? 'Creating account...' : 'Create Account' }}
        </Button>
      </form>

      <!-- Footer Links -->
      <div class="auth-footer">
        <router-link to="/login" class="auth-link">
          Already have an account? Sign in
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

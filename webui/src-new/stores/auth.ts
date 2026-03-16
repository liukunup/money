import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '../types';
import { authService } from '../services/auth.service';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(authService.getToken());
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value);

  // Actions
  async function login(username: string, password: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await authService.login(username, password);
      token.value = response.access_token;
      authService.setToken(response.access_token);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Login failed. Please check your credentials.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function register(data: { username: string; email: string; password: string }) {
    loading.value = true;
    error.value = null;
    try {
      const newUser = await authService.register(data);
      user.value = newUser;
      return newUser;
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      error.value = axiosError.response?.data?.detail || 'Registration failed. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function logout() {
    user.value = null;
    token.value = null;
    error.value = null;
    authService.logout();
  }

  function checkAuth() {
    const storedToken = authService.getToken();
    if (storedToken) {
      token.value = storedToken;
    }
  }

  function clearError() {
    error.value = null;
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
    clearError,
  };
});

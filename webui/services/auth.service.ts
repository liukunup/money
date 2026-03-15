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

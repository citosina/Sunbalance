import { defineStore } from 'pinia';
import apiClient, { extractErrorMessage, setAccessToken } from '../lib/api';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  status: 'idle' | 'loading' | 'error';
  error: string | null;
}

const TOKEN_KEY = 'sunbalance_tokens';

function persistTokens(access: string | null, refresh: string | null) {
  if (access && refresh) {
    localStorage.setItem(TOKEN_KEY, JSON.stringify({ access, refresh }));
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

function loadTokens() {
  const raw = localStorage.getItem(TOKEN_KEY);
  if (!raw) return { access: null, refresh: null };
  try {
    return JSON.parse(raw) as { access: string | null; refresh: string | null };
  } catch (error) {
    localStorage.removeItem(TOKEN_KEY);
    return { access: null, refresh: null };
  }
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => {
    const { access, refresh } = loadTokens();
    setAccessToken(access);
    return {
      accessToken: access,
      refreshToken: refresh,
      status: 'idle',
      error: null
    };
  },
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken)
  },
  actions: {
    async login(username: string, password: string) {
      this.status = 'loading';
      this.error = null;
      try {
        const response = await apiClient.post('/auth/token/', { username, password });
        this.accessToken = response.data.access;
        this.refreshToken = response.data.refresh;
        setAccessToken(this.accessToken);
        persistTokens(this.accessToken, this.refreshToken);
        this.status = 'idle';
      } catch (error) {
        this.status = 'error';
        this.error = extractErrorMessage(error);
        throw error;
      }
    },
    async refresh() {
      if (!this.refreshToken) return;
      try {
        const response = await apiClient.post('/auth/token/refresh/', {
          refresh: this.refreshToken
        });
        this.accessToken = response.data.access;
        setAccessToken(this.accessToken);
        persistTokens(this.accessToken, this.refreshToken);
      } catch (error) {
        this.logout();
        throw error;
      }
    },
    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.status = 'idle';
      this.error = null;
      setAccessToken(null);
      persistTokens(null, null);
    }
  }
});

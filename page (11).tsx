import axios, { AxiosError } from 'axios';
import Cookies from 'js-cookie';

const API_URL = 'https://zoaria-production.up.railway.app/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
});

/* ─── Request interceptor: attach JWT ─────────────────────────────────── */
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token') || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null);
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

/* ─── Response interceptor: auto-refresh on 401 ──────────────────────── */
let refreshing = false;
let queue: Array<() => void> = [];

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as any;
    if (error.response?.status === 401 && !original._retry) {
      if (refreshing) {
        return new Promise((resolve) => {
          queue.push(() => resolve(api(original)));
        });
      }
      original._retry = true;
      refreshing = true;
      try {
        const refresh = Cookies.get('refresh_token') || localStorage.getItem('refresh_token');
        if (refresh) {
          const { data } = await axios.post(`${API_URL}/auth/token/refresh/`, { refresh });
          Cookies.set('access_token', data.access);
          localStorage.setItem('access_token', data.access);
          queue.forEach((cb) => cb());
          queue = [];
          return api(original);
        }
      } catch {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      } finally {
        refreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default api;

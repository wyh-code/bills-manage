import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import authService from '@/auth/authService';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:7788/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
  apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = authService.getToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // 响应拦截器
  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

      // 401错误处理
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        // 清除token并跳转登录
        authService.onUnauthorized();
        
        return Promise.reject(error);
      }

      return Promise.reject(error);
    }
  );

export default apiClient;

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { config } from '../../config';

export const api = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (axiosConfig) => {
    const token = await AsyncStorage.getItem(config.storage.accessToken);
    if (token) {
      axiosConfig.headers.Authorization = `Bearer ${token}`;
    }
    return axiosConfig;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem(config.storage.accessToken);
      await AsyncStorage.removeItem(config.storage.user);
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: { email: string; password: string; firstName: string; lastName: string; phone: string }) =>
    api.post('/auth/register', data),

  getProfile: () => api.get('/auth/profile'),

  updateProfile: (data: any) => api.patch('/auth/profile', data),
};

// Consultations API
export const consultationsAPI = {
  getAll: () => api.get('/consultations'),

  getById: (id: string) => api.get(`/consultations/${id}`),

  create: (data: { consultantId: string; date: string; duration: number; description: string }) =>
    api.post('/consultations', data),

  cancel: (id: string) => api.patch(`/consultations/${id}/cancel`),

  getAvailableSlots: (consultantId: string, date: string) =>
    api.get(`/consultations/available-slots/${consultantId}?date=${date}`),
};

// Consultants API
export const consultantsAPI = {
  getAll: () => api.get('/consultants'),

  getById: (id: string) => api.get(`/consultants/${id}`),

  getBySpecialization: (specialization: string) =>
    api.get(`/consultants?specialization=${specialization}`),
};

// Payments API
export const paymentsAPI = {
  createPaymentIntent: (amount: number, consultationId: string) =>
    api.post('/payments/create-intent', { amount, consultationId }),

  confirmPayment: (paymentIntentId: string) =>
    api.post('/payments/confirm', { paymentIntentId }),

  getPaymentHistory: () => api.get('/payments/history'),
};

// Messages/Chat API
export const messagesAPI = {
  getConversations: () => api.get('/messages/conversations'),

  getMessages: (conversationId: string) =>
    api.get(`/messages/${conversationId}`),

  sendMessage: (conversationId: string, content: string) =>
    api.post('/messages', { conversationId, content }),
};

// Documents API
export const documentsAPI = {
  getAll: () => api.get('/documents'),

  upload: (file: FormData) =>
    api.post('/documents/upload', file, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  download: (id: string) => api.get(`/documents/${id}/download`),

  delete: (id: string) => api.delete(`/documents/${id}`),
};

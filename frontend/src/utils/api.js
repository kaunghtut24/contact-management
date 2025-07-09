import axios from 'axios';
import { API_BASE_URL } from './constants';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Debug: Log all API requests
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url, 'Base URL:', config.baseURL);

    // Add authentication header if token exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      console.error('Authentication failed - redirecting to login');
      // Clear stored auth data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Reload page to trigger login
      window.location.reload();
    } else if (error.response?.status === 403) {
      console.error('Access forbidden');
    } else if (error.response?.status === 404) {
      console.error('Resource not found');
    } else if (error.response?.status === 500) {
      console.error('Server error');
    }
    return Promise.reject(error);
  }
);

// Contact API functions
export const contactsApi = {
  // Get all contacts with optional search and filter
  getAll: (params = {}) => api.get('/contacts', { params }),
  
  // Get contact by ID
  getById: (id) => api.get(`/contacts/${id}`),
  
  // Create new contact
  create: (contact) => api.post('/contacts', contact),
  
  // Update contact
  update: (id, contact) => api.put(`/contacts/${id}`, contact),
  
  // Delete contact
  delete: (id) => api.delete(`/contacts/${id}`),
  
  // Upload file
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Export contacts
  export: () => api.get('/export', { responseType: 'blob' }),

  // Batch operations
  batchDelete: (contactIds) => api.delete('/contacts/batch', { data: contactIds }),
  batchExport: (contactIds) => api.post('/export/batch', contactIds, { responseType: 'blob' }),
};

export default api;

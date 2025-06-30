import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
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
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const executeQuery = async (query, tableName = null) => {
  const response = await api.post('/query', {
    query,
    table_name: tableName,
  });
  
  return response.data;
};

export const generateSummary = async (tableName, sampleSize = 100, summaryType = 'general') => {
  const response = await api.post('/summarize', {
    table_name: tableName,
    sample_size: sampleSize,
    summary_type: summaryType,
  });
  
  return response.data;
};

export const getTables = async () => {
  const response = await api.get('/tables');
  return response.data;
};

export const fetchPublicData = async (source, params = {}) => {
  const response = await api.post('/public-data', {
    source,
    params,
  });
  
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api; 
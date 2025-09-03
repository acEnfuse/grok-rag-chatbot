import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for file uploads
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
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to the server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// API functions
export const uploadCVAndMatch = async (formData) => {
  try {
    const response = await api.post('/upload-cv-and-match', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const uploadCV = async (formData) => {
  try {
    const response = await api.post('/upload-cv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const matchJobs = async (cvText, topK = 10) => {
  try {
    const response = await api.post('/match-jobs', {
      cv_text: cvText,
      top_k: topK,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const addJobs = async (formData) => {
  try {
    const response = await api.post('/add-jobs', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const addSampleJobs = async () => {
  try {
    const response = await api.post('/add-sample-jobs');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getCollectionStats = async () => {
  try {
    const response = await api.get('/collection-stats');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const chatWithAdvisor = async (message, chatHistory = []) => {
  try {
    const response = await api.post('/chat', {
      message,
      chat_history: chatHistory,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;

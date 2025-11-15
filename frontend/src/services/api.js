import axios from 'axios';

const API_BASE_URL = 'http://localhost:9080/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
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

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  getPreferences: () => api.get('/auth/me/preferences'),
  updatePreferences: (data) => api.put('/auth/me/preferences', data),
};

// Posts API
export const postsAPI = {
  createPost: (data) => api.post('/posts/', data),
  getPosts: (params) => api.get('/posts/', { params }),
  getPost: (postId) => api.get(`/posts/${postId}`),
  updatePost: (postId, data) => api.put(`/posts/${postId}`, data),
  deletePost: (postId) => api.delete(`/posts/${postId}`),
  getFeed: (params) => api.get('/posts/feed', { params }),
};

// Comments API
export const commentsAPI = {
  createComment: (postId, data) => api.post(`/posts/${postId}/comments`, data),
  getComments: (postId) => api.get(`/posts/${postId}/comments`),
  updateComment: (commentId, data) => api.put(`/posts/comments/${commentId}`, data),
  deleteComment: (commentId) => api.delete(`/posts/comments/${commentId}`),
};

// Likes API
export const likesAPI = {
  toggleLike: (postId) => api.post(`/posts/${postId}/like`),
  getLikeStatus: (postId) => api.get(`/posts/${postId}/like`),
};

export default api;

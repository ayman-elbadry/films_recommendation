import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
});

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (username, password) =>
  API.post('/auth/register', { username, password });

export const login = (username, password) =>
  API.post('/auth/login', { username, password });

// Recommendations
export const getPopularMovies = (limit = 10) =>
  API.get(`/recommendations/popular?limit=${limit}`);

export const getRecommendations = () =>
  API.get('/recommendations');

// Ratings
export const submitRating = (movie_id, rating) =>
  API.post('/ratings', { movie_id, rating });

export const submitBatchRatings = (ratings) =>
  API.post('/ratings/batch', { ratings });

export const getMyRatings = () =>
  API.get('/ratings');

export default API;

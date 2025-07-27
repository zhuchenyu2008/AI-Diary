import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default {
  login(password) {
    return apiClient.post('/login', { password });
  },
  getEventsTimeline() {
    return apiClient.get('/events/timeline');
  },
  createEvent(data) {
    return apiClient.post('/events', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  getSummaries(page = 1) {
    return apiClient.get(`/summaries?page=${page}`);
  },
  getSummaryByDate(date) {
    return apiClient.get(`/summaries/${date}`);
  }
};

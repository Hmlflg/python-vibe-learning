import axios from 'axios';

// Создаём axios с базовым URL из .env
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
});

// Перед каждым запросом добавляем токен в заголовок
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Если сервер вернул 401 — токен протух, удаляем и редиректим на логин
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;

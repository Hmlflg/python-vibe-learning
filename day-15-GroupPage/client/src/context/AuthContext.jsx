import { createContext, useState, useEffect, useContext } from 'react';
import api from '../api/api';

// Создаём контекст
const AuthContext = createContext(null);

// Провайдер — оборачивает всё приложение
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // При загрузке страницы проверяем есть ли сохранённый токен
    useEffect(() => {
        const token = localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');

        if (token && savedUser) {
            // Токен есть — проверяем его на сервере
            api
                .get('/api/auth/me')
                .then((res) => {
                    setUser(res.data.user);
                })
                .catch(() => {
                    // Токен невалидный — очищаем
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                })
                .finally(() => setLoading(false));
        } else {
            // Нет токена — не загружаем
            setLoading(false);
        }
    }, []);

    // Войти — сохранить user и token
    const login = (userData, token) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
    };

    // Выйти — очистить всё
    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

// Хук для удобного использования контекста
export function useAuth() {
    return useContext(AuthContext);
}

// Загружаем переменные окружения из .env
require('dotenv').config();

const express = require('express');
const cors = require('cors');

// Подключаем SQLite — база создаётся автоматически при require
require('./config/db');

const app = express();

// Разрешаем запросы с фронтенда (CORS)
app.use(cors({
    origin: process.env.CLIENT_URL,
    credentials: true,
}));

// Парсим JSON из тела запросов
app.use(express.json());

// Подключаем маршруты аутентификации
const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);

// Подключаем маршруты предметов и ДЗ
const subjectRoutes = require('./routes/subjects');
app.use('/api/subjects', subjectRoutes);

const homeworkRoutes = require('./routes/homeworks');
app.use('/api/homeworks', homeworkRoutes);

// Подключаем маршруты чата
const chatRoutes = require('./routes/chat');
app.use('/api/messages', chatRoutes);

// Простой маршрут для проверки работы сервера
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Сервер работает!' });
});

// Запускаем сервер
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 Сервер запущен на порту ${PORT}`);
});

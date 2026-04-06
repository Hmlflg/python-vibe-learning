const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { auth } = require('../middleware/auth');

const router = express.Router();

// --- РЕГИСТРАЦИЯ ---
// POST /api/auth/register
router.post('/register', async (req, res) => {
    try {
        const { login, password } = req.body;

        // Простая валидация
        if (!login || !password) {
            return res.status(400).json({ error: 'Заполните все поля' });
        }

        // Проверяем что логин свободен
        if (User.findByLogin(login)) {
            return res.status(400).json({ error: 'Логин уже занят' });
        }

        // Хешируем пароль (10 раундов — достаточно для MVP)
        const hashedPassword = await bcrypt.hash(password, 10);

        // Создаём пользователя
        const user = User.create({
            login,
            password: hashedPassword,
            role: 'user',
        });

        // Генерируем JWT токен
        const token = jwt.sign(
            { userId: user.id },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        // Отправляем пользователя (без пароля) и токен
        res.status(201).json({
            user: { id: user.id, login: user.login, role: user.role },
            token,
        });
    } catch (err) {
        console.error('Ошибка регистрации:', err);
        res.status(500).json({ error: 'Ошибка сервера' });
    }
});

// --- ЛОГИН ---
// POST /api/auth/login
router.post('/login', async (req, res) => {
    try {
        const { login, password } = req.body;

        if (!login || !password) {
            return res.status(400).json({ error: 'Заполните все поля' });
        }

        // Ищем пользователя по логину
        const user = User.findByLogin(login);

        if (!user) {
            return res.status(400).json({ error: 'Неверный логин или пароль' });
        }

        // Сравниваем пароль с хешем
        const isValid = await bcrypt.compare(password, user.password);

        if (!isValid) {
            return res.status(400).json({ error: 'Неверный логин или пароль' });
        }

        // Генерируем JWT токен
        const token = jwt.sign(
            { userId: user.id },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        res.json({
            user: { id: user.id, login: user.login, role: user.role },
            token,
        });
    } catch (err) {
        console.error('Ошибка логина:', err);
        res.status(500).json({ error: 'Ошибка сервера' });
    }
});

// --- ПОЛУЧИТЬ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ---
// GET /api/auth/me (нужен токен)
router.get('/me', auth, (req, res) => {
    res.json({
        user: { id: req.user.id, login: req.user.login, role: req.user.role },
    });
});

module.exports = router;

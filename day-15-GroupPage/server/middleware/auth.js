const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Middleware: проверяет JWT токен из заголовка Authorization
function auth(req, res, next) {
    // Получаем токен из заголовка: "Bearer <token>"
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Нет токена — войдите в аккаунт' });
    }

    // Извлекаем сам токен (убираем "Bearer ")
    const token = authHeader.split(' ')[1];

    try {
        // Расшифровываем токен и получаем userId
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        // Находим пользователя в базе
        const user = User.findById(decoded.userId);

        if (!user) {
            return res.status(401).json({ error: 'Пользователь не найден' });
        }

        // Сохраняем пользователя в req — он будет доступен в маршрутах
        req.user = user;
        next();
    } catch (err) {
        return res.status(401).json({ error: 'Невалидный токен' });
    }
}

// Middleware: проверяет что пользователь — админ
function adminOnly(req, res, next) {
    if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Только для администратора' });
    }
    next();
}

module.exports = { auth, adminOnly };

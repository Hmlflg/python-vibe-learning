const express = require('express');
const Message = require('../models/Message');
const { auth } = require('../middleware/auth');

const router = express.Router();

// --- ПОЛУЧИТЬ ИСТОРИЮ СООБЩЕНИЙ ---
// GET /api/messages (последние 50 сообщений)
router.get('/', auth, (req, res) => {
    const messages = Message.findRecent(50);
    res.json({ messages });
});

// --- ОТПРАВИТЬ СООБЩЕНИЕ ---
// POST /api/messages
router.post('/', auth, (req, res) => {
    try {
        const { text } = req.body;

        if (!text || !text.trim()) {
            return res.status(400).json({ error: 'Сообщение не может быть пустым' });
        }

        // Сохраняем сообщение с данными текущего пользователя
        const message = Message.create({
            text: text.trim(),
            userId: req.user.id,
            username: req.user.login,
        });

        res.status(201).json({ message });
    } catch (err) {
        console.error('Ошибка отправки сообщения:', err);
        res.status(500).json({ error: 'Ошибка сервера' });
    }
});

module.exports = router;

const express = require('express');
const Subject = require('../models/Subject');
const { auth, adminOnly } = require('../middleware/auth');

const router = express.Router();

// --- ПОЛУЧИТЬ ВСЕ ПРЕДМЕТЫ ---
// GET /api/subjects (доступно всем авторизованным)
router.get('/', auth, (req, res) => {
    const subjects = Subject.findAll();
    res.json({ subjects });
});

// --- СОЗДАТЬ ПРЕДМЕТ ---
// POST /api/subjects (только админ)
router.post('/', auth, adminOnly, (req, res) => {
    try {
        const { name, description } = req.body;

        if (!name) {
            return res.status(400).json({ error: 'Укажите название предмета' });
        }

        const subject = Subject.create({ name, description: description || '' });
        res.status(201).json({ subject });
    } catch (err) {
        // Если предмет с таким именем уже есть (уникальность)
        if (err.message && err.message.includes('UNIQUE')) {
            return res.status(400).json({ error: 'Предмет с таким названием уже существует' });
        }
        console.error('Ошибка создания предмета:', err);
        res.status(500).json({ error: 'Ошибка сервера' });
    }
});

// --- УДАЛИТЬ ПРЕДМЕТ ---
// DELETE /api/subjects/:id (только админ)
router.delete('/:id', auth, adminOnly, (req, res) => {
    const result = Subject.remove(req.params.id);

    if (result.changes === 0) {
        return res.status(404).json({ error: 'Предмет не найден' });
    }

    res.json({ message: 'Предмет удалён' });
});

module.exports = router;

const express = require('express');
const Homework = require('../models/Homework');
const Subject = require('../models/Subject');
const { auth, adminOnly } = require('../middleware/auth');

const router = express.Router();

// --- ПОЛУЧИТЬ ДЗ ПО ПРЕДМЕТУ ---
// GET /api/homeworks?subjectId=1 (доступно всем авторизованным)
router.get('/', auth, (req, res) => {
    const { subjectId } = req.query;

    if (!subjectId) {
        return res.status(400).json({ error: 'Укажите subjectId' });
    }

    // Проверяем что предмет существует
    const subject = Subject.findById(subjectId);
    if (!subject) {
        return res.status(404).json({ error: 'Предмет не найден' });
    }

    const homeworks = Homework.findBySubject(subjectId);
    res.json({ homeworks, subject });
});

// --- СОЗДАТЬ ДЗ ---
// POST /api/homeworks (только админ)
router.post('/', auth, adminOnly, (req, res) => {
    try {
        const { title, description, dueDate, subjectId } = req.body;

        if (!title || !description || !dueDate || !subjectId) {
            return res.status(400).json({ error: 'Заполните все поля' });
        }

        // Проверяем что предмет существует
        const subject = Subject.findById(subjectId);
        if (!subject) {
            return res.status(404).json({ error: 'Предмет не найден' });
        }

        const homework = Homework.create({ title, description, dueDate, subjectId });
        res.status(201).json({ homework });
    } catch (err) {
        console.error('Ошибка создания ДЗ:', err);
        res.status(500).json({ error: 'Ошибка сервера' });
    }
});

// --- УДАЛИТЬ ДЗ ---
// DELETE /api/homeworks/:id (только админ)
router.delete('/:id', auth, adminOnly, (req, res) => {
    const result = Homework.remove(req.params.id);

    if (result.changes === 0) {
        return res.status(404).json({ error: 'ДЗ не найдено' });
    }

    res.json({ message: 'ДЗ удалено' });
});

module.exports = router;

const db = require('../config/db');

// Получить все предметы
function findAll() {
    return db.prepare('SELECT * FROM subjects ORDER BY created_at DESC').all();
}

// Найти предмет по ID
function findById(id) {
    return db.prepare('SELECT * FROM subjects WHERE id = ?').get(id);
}

// Создать предмет
function create({ name, description = '' }) {
    const stmt = db.prepare(
        'INSERT INTO subjects (name, description) VALUES (?, ?)'
    );
    const result = stmt.run(name, description);
    return findById(result.lastInsertRowid);
}

// Удалить предмет (и все его ДЗ благодаря ON DELETE CASCADE)
function remove(id) {
    return db.prepare('DELETE FROM subjects WHERE id = ?').run(id);
}

module.exports = { findAll, findById, create, remove };

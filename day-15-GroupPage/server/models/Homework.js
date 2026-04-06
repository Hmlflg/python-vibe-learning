const db = require('../config/db');

// Получить все ДЗ по предмету
function findBySubject(subjectId) {
    return db.prepare(
        'SELECT * FROM homeworks WHERE subject_id = ? ORDER BY due_date ASC'
    ).all(subjectId);
}

// Найти ДЗ по ID
function findById(id) {
    return db.prepare('SELECT * FROM homeworks WHERE id = ?').get(id);
}

// Создать ДЗ
function create({ title, description, dueDate, subjectId }) {
    const stmt = db.prepare(
        'INSERT INTO homeworks (title, description, due_date, subject_id) VALUES (?, ?, ?, ?)'
    );
    const result = stmt.run(title, description, dueDate, subjectId);
    return findById(result.lastInsertRowid);
}

// Удалить ДЗ
function remove(id) {
    return db.prepare('DELETE FROM homeworks WHERE id = ?').run(id);
}

module.exports = { findBySubject, findById, create, remove };

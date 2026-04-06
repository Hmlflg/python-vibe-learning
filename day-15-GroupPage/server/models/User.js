const db = require('../config/db');

// Найти пользователя по логину
function findByLogin(login) {
    return db.prepare('SELECT * FROM users WHERE login = ?').get(login);
}

// Найти пользователя по ID
function findById(id) {
    return db.prepare('SELECT id, login, role, created_at FROM users WHERE id = ?').get(id);
}

// Создать нового пользователя
function create({ login, password, role = 'user' }) {
    const stmt = db.prepare(
        'INSERT INTO users (login, password, role) VALUES (?, ?, ?)'
    );
    const result = stmt.run(login, password, role);
    return findById(result.lastInsertRowid);
}

module.exports = { findByLogin, findById, create };

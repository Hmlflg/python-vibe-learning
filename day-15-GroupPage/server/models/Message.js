const db = require('../config/db');

// Получить последние N сообщений (для истории чата)
function findRecent(limit = 100) {
    return db.prepare(
        'SELECT * FROM messages ORDER BY created_at ASC LIMIT ?'
    ).all(limit);
}

// Создать сообщение
function create({ text, userId, username }) {
    const stmt = db.prepare(
        'INSERT INTO messages (text, user_id, username) VALUES (?, ?, ?)'
    );
    const result = stmt.run(text, userId, username);
    return db.prepare('SELECT * FROM messages WHERE id = ?').get(result.lastInsertRowid);
}

module.exports = { findRecent, create };

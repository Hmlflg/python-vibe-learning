const db = require('../config/db');

function normalizeUser(user) {
  if (!user) {
    return null;
  }

  return {
    ...user,
    is_activated: Boolean(user.is_activated),
  };
}

function findByLogin(login) {
  const user = db.prepare('SELECT * FROM users WHERE login = ?').get(login);
  return normalizeUser(user);
}

function findById(id) {
  const user = db
    .prepare('SELECT id, login, role, created_at, is_activated FROM users WHERE id = ?')
    .get(id);
  return normalizeUser(user);
}

function findPendingByLogin(login) {
  const user = db
    .prepare('SELECT * FROM users WHERE login = ? AND is_activated = 0')
    .get(login);
  return normalizeUser(user);
}

function create({ login, password, role = 'user', isActivated = true }) {
  const stmt = db.prepare(
    'INSERT INTO users (login, password, role, is_activated) VALUES (?, ?, ?, ?)'
  );
  const result = stmt.run(login, password, role, isActivated ? 1 : 0);
  return findById(result.lastInsertRowid);
}

function activate({ id, password }) {
  db.prepare('UPDATE users SET password = ?, is_activated = 1 WHERE id = ?').run(password, id);
  return findById(id);
}

module.exports = { findByLogin, findById, findPendingByLogin, create, activate };

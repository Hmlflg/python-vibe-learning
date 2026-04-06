const Database = require('better-sqlite3');
const path = require('path');

// Путь к файлу базы данных (в папке server)
const DB_PATH = path.join(__dirname, '..', 'database.db');

// Открываем (или создаём) базу данных
const db = new Database(DB_PATH);

// Включаем режим WAL для лучшей производительности
db.pragma('journal_mode = WAL');

// Создаём таблицы если их ещё нет
db.exec(`
  -- Таблица пользователей
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- Таблица предметов
  CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- Таблица домашних заданий
  CREATE TABLE IF NOT EXISTS homeworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    due_date TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
  );

  -- Таблица сообщений чата
  CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

console.log('✅ SQLite база данных готова');

module.exports = db;

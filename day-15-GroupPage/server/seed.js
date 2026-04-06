// Скрипт для заполнения базы начальными данными
// Запускать один раз: cd server && node seed.js

require('dotenv').config();
const db = require('./config/db');
const bcrypt = require('bcrypt');

async function seed() {
    console.log('🌱 Заполняю базу данными...');

    // 1. Создаём админа (если ещё нет)
    const adminExists = db.prepare('SELECT id FROM users WHERE login = ?').get('admin');
    if (!adminExists) {
        const hashedPassword = await bcrypt.hash('admin123', 10);
        db.prepare('INSERT INTO users (login, password, role) VALUES (?, ?, ?)').run(
            'admin', hashedPassword, 'admin'
        );
        console.log('  ✅ Админ создан: login=admin, password=admin123');
    } else {
        console.log('  ⏭️  Админ уже есть');
    }

    // 2. Создаём предметы (если база пустая)
    const subjectsCount = db.prepare('SELECT COUNT(*) as count FROM subjects').get().count;
    if (subjectsCount === 0) {
        const subjectsData = [
            { name: 'Математика', description: 'Высшая математика, линейная алгебра' },
            { name: 'Физика', description: 'Общая физика, механика' },
            { name: 'Программирование', description: 'Основы программирования на Python' },
            { name: 'Английский язык', description: 'Английский для IT' },
        ];

        const stmt = db.prepare('INSERT INTO subjects (name, description) VALUES (?, ?)');
        const subjectIds = [];
        for (const s of subjectsData) {
            const result = stmt.run(s.name, s.description);
            subjectIds.push(result.lastInsertRowid);
        }
        console.log(`  ✅ Добавлено ${subjectsData.length} предметов`);

        // 3. Добавляем примеры ДЗ (используем реальные ID)
        const homeworks = [
            { title: 'Интегралы', description: 'Решить задачи 1-15 из задачника', dueDate: '2026-04-20', subjectId: subjectIds[0] },
            { title: 'Матрицы', description: 'Найти определитель матрицы 3x3', dueDate: '2026-04-25', subjectId: subjectIds[0] },
            { title: 'Законы Ньютона', description: 'Решить 5 задач на второй закон', dueDate: '2026-04-18', subjectId: subjectIds[1] },
            { title: 'Циклы в Python', description: 'Написать программу с циклом for и while', dueDate: '2026-04-22', subjectId: subjectIds[2] },
            { title: 'Essay: My Future', description: 'Написать эссе на 200 слов', dueDate: '2026-04-30', subjectId: subjectIds[3] },
        ];

        const hwStmt = db.prepare('INSERT INTO homeworks (title, description, due_date, subject_id) VALUES (?, ?, ?, ?)');
        for (const h of homeworks) {
            hwStmt.run(h.title, h.description, h.dueDate, h.subjectId);
        }
        console.log(`  ✅ Добавлено ${homeworks.length} домашних заданий`);
    } else {
        console.log('  ⏭️  Предметы уже есть');
    }

    console.log('🎉 Готово!');
}

seed().catch(console.error);

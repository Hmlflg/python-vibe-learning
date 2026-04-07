# Group Page

Веб-приложение для студенческой группы: предметы, домашние задания, общий чат.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Корневые зависимости (concurrently)
npm install

# Сервер
cd server && npm install

# Клиент
cd ../client && npm install
```

### 2. Заполнение базы данных

```bash
cd server
npm run seed
```

Это создаст:
- **Админа:** login `admin`, password `admin123`
- **4 предмета:** Математика, Физика, Программирование, Английский язык
- **5 домашних заданий** с датами сдачи

### 3. Запуск

```bash
# В корневой папке:
npm run dev
```

Откроется:
- **Фронтенд:** http://localhost:5173
- **Бэкенд:** http://localhost:5000

## 📁 Структура проекта

```
day-15-GroupPage/
├── client/              # React + Vite фронтенд
│   ├── src/
│   │   ├── api/         # Axios с авто-подстановкой JWT
│   │   ├── context/     # AuthContext (авторизация)
│   │   ├── pages/       # Страницы: Login, Register, Dashboard
│   │   ├── App.jsx      # Роутер + защищённые маршруты
│   │   └── index.css    # Стили Dashboard
│   └── .env             # VITE_API_URL
├── server/              # Express + SQLite бэкенд
│   ├── config/          # Подключение к БД
│   ├── middleware/      # auth.js (JWT + adminOnly)
│   ├── models/          # User, Subject, Homework, Message
│   ├── routes/          # auth, subjects, homeworks, chat
│   ├── database.db      # SQLite файл (не в git)
│   ├── seed.js          # Начальные данные
│   └── index.js         # Точка входа
└── package.json         # Скрипты запуска
```

## 🔐 Как работает авторизация

1. **Админ** создаёт логин для студента через вкладку «Админка»
2. **Студент** заходит на `/register`, вводит выданный логин и придумывает пароль
3. После активации — вход по логину + паролю
4. JWT токен хранится в `localStorage`, проверяется при каждом запросе

## 🛠 Технологии

| Слой | Технологии |
|---|---|
| Frontend | React 18, Vite, React Router, Axios |
| Backend | Node.js, Express, better-sqlite3 |
| Auth | JWT (jsonwebtoken), bcrypt |
| Chat | Polling (опрос каждые 3 сек) |
| Database | SQLite (один файл) |

##  Деплой (бесплатно)

### База данных
SQLite хранится в файле `server/database.db`. При деплое файл создаётся автоматически через `npm run seed`.

### Backend → Render (render.com)

1. Зарегистрируйся на https://render.com
2. **New → Web Service** → подключи GitHub репозиторий
3. Настройки:
   - **Root Directory:** `day-15-GroupPage/server`
   - **Build Command:** `npm install`
   - **Start Command:** `npm start && npm run seed`
4. В **Environment** добавь:
   - `JWT_SECRET` — любая длинная строка
   - `CLIENT_URL` — URL фронтенда (после деплоя)
   - `PORT` — Render сам установит

### Frontend → Vercel (vercel.com)

1. Зарегистрируйся на https://vercel.com
2. **New Project** → импортируй репозиторий
3. Настройки:
   - **Root Directory:** `day-15-GroupPage/client`
   - **Framework Preset:** Vite
4. В **Environment Variables** добавь:
   - `VITE_API_URL` — URL бэкенда на Render (например `https://your-app.onrender.com`)

### После деплоя

1. Скопируй URL фронтенда из Vercel
2. Обнови `CLIENT_URL` в Render → redeploy
3. Готово!

## 🔄 Обновление данных

```bash
# Полная очистка и пересоздание базы:
cd server
npm run seed:reset
```

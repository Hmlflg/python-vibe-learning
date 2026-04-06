const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { auth, adminOnly } = require('../middleware/auth');

const router = express.Router();

function createToken(userId) {
  return jwt.sign({ userId }, process.env.JWT_SECRET, { expiresIn: '7d' });
}

router.post('/register', async (req, res) => {
  try {
    const login = req.body.login?.trim();
    const password = req.body.password?.trim();

    if (!login || !password) {
      return res.status(400).json({ error: 'Заполните все поля' });
    }

    if (password.length < 4) {
      return res.status(400).json({ error: 'Пароль должен быть не короче 4 символов' });
    }

    const pendingUser = User.findPendingByLogin(login);

    if (!pendingUser) {
      const existingUser = User.findByLogin(login);

      if (existingUser?.is_activated) {
        return res.status(400).json({ error: 'Этот логин уже активирован. Войдите в аккаунт.' });
      }

      return res.status(400).json({ error: 'Такого выданного логина нет. Обратитесь к администратору.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = User.activate({ id: pendingUser.id, password: hashedPassword });
    const token = createToken(user.id);

    res.status(201).json({
      user: { id: user.id, login: user.login, role: user.role },
      token,
    });
  } catch (err) {
    console.error('Registration error:', err);
    res.status(500).json({ error: 'Ошибка сервера' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const login = req.body.login?.trim();
    const password = req.body.password?.trim();

    if (!login || !password) {
      return res.status(400).json({ error: 'Заполните все поля' });
    }

    const user = User.findByLogin(login);

    if (!user) {
      return res.status(400).json({ error: 'Неверный логин или пароль' });
    }

    if (!user.is_activated) {
      return res.status(400).json({ error: 'Сначала завершите регистрацию и задайте пароль.' });
    }

    const isValid = await bcrypt.compare(password, user.password);

    if (!isValid) {
      return res.status(400).json({ error: 'Неверный логин или пароль' });
    }

    const token = createToken(user.id);

    res.json({
      user: { id: user.id, login: user.login, role: user.role },
      token,
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Ошибка сервера' });
  }
});

router.get('/me', auth, (req, res) => {
  res.json({
    user: { id: req.user.id, login: req.user.login, role: req.user.role },
  });
});

router.post('/users', auth, adminOnly, (req, res) => {
  try {
    const login = req.body.login?.trim();
    const role = req.body.role === 'admin' ? 'admin' : 'user';

    if (!login) {
      return res.status(400).json({ error: 'Укажите логин' });
    }

    if (User.findByLogin(login)) {
      return res.status(400).json({ error: 'Такой логин уже существует' });
    }

    const user = User.create({
      login,
      password: '',
      role,
      isActivated: false,
    });

    res.status(201).json({
      user: { id: user.id, login: user.login, role: user.role, isActivated: user.is_activated },
      message: 'Логин создан. Передайте его студенту для активации.',
    });
  } catch (err) {
    console.error('Create pending user error:', err);
    res.status(500).json({ error: 'Ошибка сервера' });
  }
});

module.exports = router;

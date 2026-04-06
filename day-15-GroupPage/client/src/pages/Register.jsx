import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';

export default function Register() {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login: authLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await api.post('/api/auth/register', { login, password });
      authLogin(res.data.user, res.data.token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Ошибка активации аккаунта');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: '#f5f5f5',
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: '#fff',
          padding: 30,
          borderRadius: 12,
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          width: 360,
        }}
      >
        <h2 style={{ marginBottom: 12, textAlign: 'center' }}>Активация аккаунта</h2>
        <p style={{ marginBottom: 20, textAlign: 'center', color: '#555', fontSize: 14 }}>
          Введите логин, который выдал администратор, и придумайте свой пароль.
        </p>

        {error && (
          <div
            style={{
              background: '#fee2e2',
              color: '#dc2626',
              padding: '8px 12px',
              borderRadius: 6,
              marginBottom: 15,
              fontSize: 14,
            }}
          >
            {error}
          </div>
        )}

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 14 }}>Выданный логин</label>
          <input
            type="text"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
            placeholder="Например, ivanov.i"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: 6,
              fontSize: 14,
            }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 14 }}>Новый пароль</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={4}
            placeholder="Минимум 4 символа"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: 6,
              fontSize: 14,
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '10px',
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            fontSize: 14,
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Активация...' : 'Активировать аккаунт'}
        </button>

        <p style={{ marginTop: 15, textAlign: 'center', fontSize: 14 }}>
          Аккаунт уже активирован? <Link to="/login">Войти</Link>
        </p>
      </form>
    </div>
  );
}

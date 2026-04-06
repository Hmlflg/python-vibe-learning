import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Subjects from './pages/Subjects';
import Homework from './pages/Homework';
import Chat from './pages/Chat';

// Компонент-обёртка: если не авторизован — редирект на /login
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  // Пока проверяем токен — показываем загрузку
  if (loading) {
    return <div style={{ padding: 20 }}>Загрузка...</div>;
  }

  // Нет пользователя — на логин
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Авторизован — показываем страницу
  return children;
}

// Навигационная панель (показывается только авторизованным)
function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 20px',
      borderBottom: '1px solid #ddd',
      background: '#fff',
    }}>
      <div style={{ display: 'flex', gap: 20 }}>
        <Link to="/">Предметы</Link>
        <Link to="/chat">Чат</Link>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 15 }}>
        <span>👤 {user.login} {user.role === 'admin' && '(админ)'}</span>
        <button onClick={handleLogout}>Выйти</button>
      </div>
    </nav>
  );
}

// Layout для авторизованных страниц
function AppLayout({ children }) {
  return (
    <div>
      <Navbar />
      <main style={{ padding: 20 }}>{children}</main>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      {/* Публичные маршруты */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Защищённые маршруты */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Subjects />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/subjects/:id"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Homework />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Chat />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* Неизвестный URL — редирект на главную */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

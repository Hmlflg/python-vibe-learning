import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

function formatTime(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function isOverdue(dueDate) {
  return new Date(dueDate) < new Date();
}

export default function Dashboard() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const [activeTab, setActiveTab] = useState('study');
  const [subjects, setSubjects] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState(null);
  const [subject, setSubject] = useState(null);
  const [homeworks, setHomeworks] = useState([]);
  const [messages, setMessages] = useState([]);

  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [loadingHomeworks, setLoadingHomeworks] = useState(false);
  const [chatError, setChatError] = useState('');
  const [pageError, setPageError] = useState('');
  const [pageNotice, setPageNotice] = useState('');

  const [newSubjectName, setNewSubjectName] = useState('');
  const [newSubjectDesc, setNewSubjectDesc] = useState('');
  const [newHomeworkTitle, setNewHomeworkTitle] = useState('');
  const [newHomeworkDesc, setNewHomeworkDesc] = useState('');
  const [newHomeworkDue, setNewHomeworkDue] = useState('');
  const [newStudentLogin, setNewStudentLogin] = useState('');
  const [messageText, setMessageText] = useState('');

  const chatFeedRef = useRef(null);

  useEffect(() => {
    loadSubjects();
    loadMessages();
  }, []);

  useEffect(() => {
    if (!selectedSubjectId) {
      setSubject(null);
      setHomeworks([]);
      return;
    }

    loadHomeworks(selectedSubjectId);
  }, [selectedSubjectId]);

  useEffect(() => {
    const interval = setInterval(loadMessages, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const feed = chatFeedRef.current;
    if (!feed) {
      return;
    }

    feed.scrollTop = feed.scrollHeight;
  }, [messages]);

  function resetBanner(type = 'all') {
    if (type === 'all' || type === 'error') {
      setPageError('');
      setChatError('');
    }

    if (type === 'all' || type === 'notice') {
      setPageNotice('');
    }
  }

  async function loadSubjects(preferredSubjectId) {
    try {
      resetBanner('error');
      setLoadingSubjects(true);
      const res = await api.get('/api/subjects');
      const nextSubjects = res.data.subjects;
      setSubjects(nextSubjects);

      if (nextSubjects.length === 0) {
        setSelectedSubjectId(null);
        return;
      }

      const nextSelectedId =
        preferredSubjectId ??
        (nextSubjects.some((item) => item.id === selectedSubjectId)
          ? selectedSubjectId
          : nextSubjects[0].id);

      setSelectedSubjectId(nextSelectedId);
    } catch (_err) {
      setPageError('Не удалось загрузить предметы');
    } finally {
      setLoadingSubjects(false);
    }
  }

  async function loadHomeworks(subjectId) {
    try {
      resetBanner('error');
      setLoadingHomeworks(true);
      const res = await api.get(`/api/homeworks?subjectId=${subjectId}`);
      setSubject(res.data.subject);
      setHomeworks(res.data.homeworks);
    } catch (_err) {
      setPageError('Не удалось загрузить домашние задания');
      setSubject(null);
      setHomeworks([]);
    } finally {
      setLoadingHomeworks(false);
    }
  }

  async function loadMessages() {
    try {
      const res = await api.get('/api/messages');
      setMessages(res.data.messages);
    } catch (_err) {
      // Ошибки polling не показываем, чтобы не мешать основной работе.
    }
  }

  async function handleCreateStudent(e) {
    e.preventDefault();
    if (!newStudentLogin.trim()) {
      return;
    }

    try {
      resetBanner();
      const res = await api.post('/api/auth/users', {
        login: newStudentLogin.trim(),
      });
      setNewStudentLogin('');
      setPageNotice(`Логин "${res.data.user.login}" создан. Теперь студент может активировать его на странице регистрации.`);
    } catch (err) {
      setPageError(err.response?.data?.error || 'Не удалось создать логин студента');
    }
  }

  async function handleAddSubject(e) {
    e.preventDefault();
    if (!newSubjectName.trim()) {
      return;
    }

    try {
      resetBanner();
      const res = await api.post('/api/subjects', {
        name: newSubjectName.trim(),
        description: newSubjectDesc.trim(),
      });
      const createdSubject = res.data.subject;
      setNewSubjectName('');
      setNewSubjectDesc('');
      setPageNotice(`Предмет "${createdSubject.name}" добавлен.`);
      await loadSubjects(createdSubject.id);
    } catch (err) {
      setPageError(err.response?.data?.error || 'Ошибка при создании предмета');
    }
  }

  async function handleDeleteSubject(subjectId, subjectName) {
    if (!window.confirm(`Удалить предмет "${subjectName}"? Все домашние задания тоже будут удалены.`)) {
      return;
    }

    try {
      resetBanner();
      await api.delete(`/api/subjects/${subjectId}`);
      setPageNotice(`Предмет "${subjectName}" удалён.`);
      await loadSubjects();
    } catch (err) {
      setPageError(err.response?.data?.error || 'Ошибка при удалении предмета');
    }
  }

  async function handleAddHomework(e) {
    e.preventDefault();
    if (!selectedSubjectId || !newHomeworkTitle.trim() || !newHomeworkDesc.trim() || !newHomeworkDue) {
      return;
    }

    try {
      resetBanner();
      await api.post('/api/homeworks', {
        title: newHomeworkTitle.trim(),
        description: newHomeworkDesc.trim(),
        dueDate: newHomeworkDue,
        subjectId: selectedSubjectId,
      });
      setNewHomeworkTitle('');
      setNewHomeworkDesc('');
      setNewHomeworkDue('');
      setPageNotice('Домашнее задание добавлено.');
      await loadHomeworks(selectedSubjectId);
    } catch (err) {
      setPageError(err.response?.data?.error || 'Ошибка при создании домашнего задания');
    }
  }

  async function handleDeleteHomework(homeworkId, homeworkTitle) {
    if (!window.confirm(`Удалить домашнее задание "${homeworkTitle}"?`)) {
      return;
    }

    try {
      resetBanner();
      await api.delete(`/api/homeworks/${homeworkId}`);
      setPageNotice(`Домашнее задание "${homeworkTitle}" удалено.`);
      await loadHomeworks(selectedSubjectId);
    } catch (err) {
      setPageError(err.response?.data?.error || 'Ошибка при удалении домашнего задания');
    }
  }

  async function handleSendMessage(e) {
    e.preventDefault();
    if (!messageText.trim()) {
      return;
    }

    try {
      setChatError('');
      await api.post('/api/messages', { text: messageText.trim() });
      setMessageText('');
      await loadMessages();
    } catch (err) {
      setChatError(err.response?.data?.error || 'Ошибка отправки сообщения');
    }
  }

  function renderStudyTab() {
    return (
      <section className="dashboard-grid">
        <aside className="panel panel-subjects">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Навигация</p>
              <h2>Предметы</h2>
            </div>
          </div>

          <div className="subject-list">
            {loadingSubjects ? (
              <p className="muted-text">Загрузка предметов...</p>
            ) : subjects.length === 0 ? (
              <p className="muted-text">Пока нет предметов</p>
            ) : (
              subjects.map((item) => {
                const isActive = item.id === selectedSubjectId;
                return (
                  <div
                    key={item.id}
                    className={`subject-card${isActive ? ' active' : ''}`}
                    onClick={() => setSelectedSubjectId(item.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedSubjectId(item.id);
                      }
                    }}
                  >
                    <div className="subject-card-main">
                      <strong>{item.name}</strong>
                      {item.description && <span>{item.description}</span>}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>

        <main className="panel panel-homeworks">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Выбранный предмет</p>
              <h2>{subject?.name || 'Домашка'}</h2>
            </div>
          </div>

          {subject?.description && <p className="subject-description">{subject.description}</p>}

          {!selectedSubjectId ? (
            <p className="muted-text">Выберите предмет слева</p>
          ) : loadingHomeworks ? (
            <p className="muted-text">Загрузка домашки...</p>
          ) : homeworks.length === 0 ? (
            <p className="muted-text">По этому предмету пока нет домашнего задания</p>
          ) : (
            <div className="homework-list">
              {homeworks.map((item) => {
                const overdue = isOverdue(item.due_date);
                return (
                  <article key={item.id} className={`homework-card${overdue ? ' overdue' : ''}`}>
                    <div className="homework-card-top">
                      <div>
                        <h3>{item.title}</h3>
                        <p>{item.description}</p>
                      </div>
                    </div>
                    <div className={`homework-meta${overdue ? ' danger' : ''}`}>
                      {overdue ? 'Просрочено: ' : 'Сдать до: '}
                      {formatDate(item.due_date)}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </main>

        <section className="panel panel-chat">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Общий канал</p>
              <h2>Чат группы</h2>
            </div>
          </div>

          {chatError && <div className="alert alert-error">{chatError}</div>}

          <div className="chat-feed" ref={chatFeedRef}>
            {messages.length === 0 ? (
              <p className="muted-text chat-empty">Сообщений пока нет. Можно начать первым.</p>
            ) : (
              messages.map((item) => {
                const isMine = item.user_id === user?.id;
                return (
                  <div key={item.id} className={`chat-message${isMine ? ' mine' : ''}`}>
                    {!isMine && <div className="chat-author">{item.username}</div>}
                    <div className="chat-text">{item.text}</div>
                    <div className="chat-time">{formatTime(item.created_at)}</div>
                  </div>
                );
              })
            )}
          </div>

          <form className="chat-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              placeholder="Написать сообщение..."
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
            />
            <button type="submit" className="primary-button">Отправить</button>
          </form>
        </section>
      </section>
    );
  }

  function renderAdminTab() {
    return (
      <section className="admin-grid">
        <div className="admin-sidebar">
          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Предметы</p>
                <h2>Управление предметами</h2>
              </div>
            </div>

            <form className="stack-form" onSubmit={handleAddSubject}>
              <input
                type="text"
                placeholder="Новый предмет"
                value={newSubjectName}
                onChange={(e) => setNewSubjectName(e.target.value)}
                required
              />
              <input
                type="text"
                placeholder="Описание"
                value={newSubjectDesc}
                onChange={(e) => setNewSubjectDesc(e.target.value)}
              />
              <button type="submit" className="primary-button">Добавить предмет</button>
            </form>

            <div className="subject-list">
              {loadingSubjects ? (
                <p className="muted-text">Загрузка предметов...</p>
              ) : subjects.length === 0 ? (
                <p className="muted-text">Пока нет предметов</p>
              ) : (
                subjects.map((item) => (
                  <div key={item.id} className="subject-card admin-card">
                    <div className="subject-card-main">
                      <strong>{item.name}</strong>
                      {item.description && <span>{item.description}</span>}
                    </div>
                    <button
                      type="button"
                      className="ghost-danger-button"
                      onClick={() => handleDeleteSubject(item.id, item.name)}
                    >
                      Удалить
                    </button>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Пользователи</p>
                <h2>Выдать логин</h2>
              </div>
            </div>

            <form className="stack-form" onSubmit={handleCreateStudent}>
              <div className="form-note">
                Создай логин для студента. Пароль он задаст сам на странице регистрации.
              </div>
              <input
                type="text"
                placeholder="Логин студента"
                value={newStudentLogin}
                onChange={(e) => setNewStudentLogin(e.target.value)}
                required
              />
              <button type="submit" className="primary-button">Выдать логин</button>
            </form>
          </section>
        </div>

        <section className="panel admin-homework-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Домашка</p>
              <h2>Управление заданиями</h2>
            </div>
          </div>

          <div className="form-note">
            Сначала выбери предмет. Сейчас выбран: <strong>{subject?.name || 'не выбран'}</strong>
          </div>

          <div className="subject-pills">
            {subjects.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`subject-pill${item.id === selectedSubjectId ? ' active' : ''}`}
                onClick={() => setSelectedSubjectId(item.id)}
              >
                {item.name}
              </button>
            ))}
          </div>

          {selectedSubjectId && (
            <form className="stack-form" onSubmit={handleAddHomework}>
              <input
                type="text"
                placeholder="Название домашнего задания"
                value={newHomeworkTitle}
                onChange={(e) => setNewHomeworkTitle(e.target.value)}
                required
              />
              <input
                type="date"
                value={newHomeworkDue}
                onChange={(e) => setNewHomeworkDue(e.target.value)}
                required
              />
              <textarea
                rows={3}
                placeholder="Описание задания"
                value={newHomeworkDesc}
                onChange={(e) => setNewHomeworkDesc(e.target.value)}
                required
              />
              <button type="submit" className="primary-button">Добавить домашку</button>
            </form>
          )}

          {!selectedSubjectId ? (
            <p className="muted-text">Выберите предмет для управления домашкой</p>
          ) : loadingHomeworks ? (
            <p className="muted-text">Загрузка домашки...</p>
          ) : homeworks.length === 0 ? (
            <p className="muted-text">По выбранному предмету пока нет заданий</p>
          ) : (
            <div className="homework-list">
              {homeworks.map((item) => (
                <article key={item.id} className={`homework-card${isOverdue(item.due_date) ? ' overdue' : ''}`}>
                  <div className="homework-card-top">
                    <div>
                      <h3>{item.title}</h3>
                      <p>{item.description}</p>
                    </div>
                    <button
                      type="button"
                      className="ghost-danger-button"
                      onClick={() => handleDeleteHomework(item.id, item.title)}
                    >
                      Удалить
                    </button>
                  </div>
                  <div className={`homework-meta${isOverdue(item.due_date) ? ' danger' : ''}`}>
                    {isOverdue(item.due_date) ? 'Просрочено: ' : 'Сдать до: '}
                    {formatDate(item.due_date)}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    );
  }

  return (
    <div className="dashboard-shell">
      <header className="dashboard-topbar">
        <div>
          <p className="dashboard-eyebrow">Group Page</p>
          <h1 className="dashboard-title">Кабинет группы</h1>
        </div>
        <div className="dashboard-user">
          <span>{user?.login}</span>
          {isAdmin && <span className="role-badge">admin</span>}
        </div>
      </header>

      {isAdmin && (
        <div className="tab-switcher">
          <button
            type="button"
            className={`tab-button${activeTab === 'study' ? ' active' : ''}`}
            onClick={() => setActiveTab('study')}
          >
            Основная страница
          </button>
          <button
            type="button"
            className={`tab-button${activeTab === 'admin' ? ' active' : ''}`}
            onClick={() => setActiveTab('admin')}
          >
            Админка
          </button>
        </div>
      )}

      {pageError && <div className="alert alert-error">{pageError}</div>}
      {pageNotice && <div className="alert alert-success">{pageNotice}</div>}

      {isAdmin && activeTab === 'admin' ? renderAdminTab() : renderStudyTab()}
    </div>
  );
}

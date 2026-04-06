import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';

export default function Homework() {
    const { id } = useParams(); // ID предмета из URL
    const { user } = useAuth();
    const [subject, setSubject] = useState(null);
    const [homeworks, setHomeworks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Поля для добавления ДЗ
    const [newTitle, setNewTitle] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newDue, setNewDue] = useState('');

    const isAdmin = user?.role === 'admin';

    // Загружаем ДЗ при открытии страницы
    useEffect(() => {
        loadHomeworks();
    }, [id]);

    const loadHomeworks = async () => {
        try {
            const res = await api.get(`/api/homeworks?subjectId=${id}`);
            setSubject(res.data.subject);
            setHomeworks(res.data.homeworks);
        } catch (err) {
            setError('Не удалось загрузить ДЗ');
        } finally {
            setLoading(false);
        }
    };

    // Добавить ДЗ (только админ)
    const handleAdd = async (e) => {
        e.preventDefault();
        if (!newTitle.trim() || !newDesc.trim() || !newDue) return;

        try {
            await api.post('/api/homeworks', {
                title: newTitle,
                description: newDesc,
                dueDate: newDue,
                subjectId: id,
            });
            setNewTitle('');
            setNewDesc('');
            setNewDue('');
            loadHomeworks();
        } catch (err) {
            setError(err.response?.data?.error || 'Ошибка при создании');
        }
    };

    // Удалить ДЗ (только админ)
    const handleDelete = async (hwId, title) => {
        if (!confirm(`Удалить ДЗ "${title}"?`)) return;

        try {
            await api.delete(`/api/homeworks/${hwId}`);
            loadHomeworks();
        } catch (err) {
            setError('Ошибка при удалении');
        }
    };

    // Форматируем дату сдачи
    const formatDate = (dateStr) => {
        const d = new Date(dateStr);
        return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
    };

    // Проверяем просрочено ли ДЗ
    const isOverdue = (dueDate) => {
        return new Date(dueDate) < new Date();
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            {/* Заголовок с кнопкой назад */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
                <Link to="/" style={{ fontSize: 20, textDecoration: 'none' }}>←</Link>
                <h2 style={{ margin: 0 }}>
                    {subject?.name || 'Домашние задания'}
                </h2>
            </div>

            {error && (
                <div style={{
                    background: '#fee2e2',
                    color: '#dc2626',
                    padding: '8px 12px',
                    borderRadius: 6,
                    marginBottom: 15,
                    fontSize: 14,
                }}>
                    {error}
                </div>
            )}

            {/* Форма добавления ДЗ (только для админа) */}
            {isAdmin && (
                <form onSubmit={handleAdd} style={{
                    background: '#f9fafb',
                    padding: 15,
                    borderRadius: 8,
                    marginBottom: 20,
                    border: '1px solid #e5e7eb',
                }}>
                    <h3 style={{ marginBottom: 10, fontSize: 16 }}>Добавить ДЗ</h3>
                    <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
                        <input
                            type="text"
                            placeholder="Название"
                            value={newTitle}
                            onChange={(e) => setNewTitle(e.target.value)}
                            required
                            style={{ flex: 1, padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
                        />
                        <input
                            type="date"
                            value={newDue}
                            onChange={(e) => setNewDue(e.target.value)}
                            required
                            style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
                        />
                        <button type="submit" style={{ background: '#2563eb', color: '#fff', border: 'none' }}>
                            Добавить
                        </button>
                    </div>
                    <textarea
                        placeholder="Описание задания"
                        value={newDesc}
                        onChange={(e) => setNewDesc(e.target.value)}
                        required
                        rows={2}
                        style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, resize: 'vertical' }}
                    />
                </form>
            )}

            {/* Список ДЗ */}
            {homeworks.length === 0 ? (
                <p style={{ color: '#666' }}>Пока нет домашних заданий</p>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {homeworks.map((hw) => (
                        <div
                            key={hw.id}
                            style={{
                                padding: '12px 16px',
                                background: '#fff',
                                borderRadius: 8,
                                border: '1px solid #e5e7eb',
                                borderLeft: isOverdue(hw.due_date) ? '3px solid #dc2626' : '3px solid #2563eb',
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div style={{ flex: 1 }}>
                                    <strong>{hw.title}</strong>
                                    <p style={{ margin: '5px 0', color: '#555', fontSize: 14 }}>{hw.description}</p>
                                    <span style={{
                                        fontSize: 13,
                                        color: isOverdue(hw.due_date) ? '#dc2626' : '#666',
                                        fontWeight: isOverdue(hw.due_date) ? 'bold' : 'normal',
                                    }}>
                                        {isOverdue(hw.due_date) ? '⚠️ Просрочено: ' : '📅 Сдать до: '}
                                        {formatDate(hw.due_date)}
                                    </span>
                                </div>

                                {/* Кнопка удаления (только для админа) */}
                                {isAdmin && (
                                    <button
                                        onClick={() => handleDelete(hw.id, hw.title)}
                                        style={{
                                            background: '#fee2e2',
                                            color: '#dc2626',
                                            border: 'none',
                                            padding: '4px 12px',
                                            borderRadius: 4,
                                            fontSize: 13,
                                            marginLeft: 10,
                                        }}
                                    >
                                        Удалить
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

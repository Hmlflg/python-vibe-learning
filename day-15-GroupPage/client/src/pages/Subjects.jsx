import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';

export default function Subjects() {
    const { user } = useAuth();
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Поля для добавления предмета
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');

    const isAdmin = user?.role === 'admin';

    // Загружаем предметы при открытии страницы
    useEffect(() => {
        loadSubjects();
    }, []);

    const loadSubjects = async () => {
        try {
            const res = await api.get('/api/subjects');
            setSubjects(res.data.subjects);
        } catch (err) {
            setError('Не удалось загрузить предметы');
        } finally {
            setLoading(false);
        }
    };

    // Добавить предмет (только админ)
    const handleAdd = async (e) => {
        e.preventDefault();
        if (!newName.trim()) return;

        try {
            await api.post('/api/subjects', { name: newName, description: newDesc });
            setNewName('');
            setNewDesc('');
            loadSubjects(); // Перезагружаем список
        } catch (err) {
            setError(err.response?.data?.error || 'Ошибка при создании');
        }
    };

    // Удалить предмет (только админ)
    const handleDelete = async (id, name) => {
        if (!confirm(`Удалить предмет "${name}"? Все ДЗ тоже будут удалены.`)) return;

        try {
            await api.delete(`/api/subjects/${id}`);
            loadSubjects();
        } catch (err) {
            setError('Ошибка при удалении');
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h2 style={{ marginBottom: 20 }}>Предметы</h2>

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

            {/* Форма добавления предмета (только для админа) */}
            {isAdmin && (
                <form onSubmit={handleAdd} style={{
                    background: '#f9fafb',
                    padding: 15,
                    borderRadius: 8,
                    marginBottom: 20,
                    border: '1px solid #e5e7eb',
                }}>
                    <h3 style={{ marginBottom: 10, fontSize: 16 }}>Добавить предмет</h3>
                    <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
                        <input
                            type="text"
                            placeholder="Название"
                            value={newName}
                            onChange={(e) => setNewName(e.target.value)}
                            required
                            style={{ flex: 1, padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
                        />
                        <input
                            type="text"
                            placeholder="Описание (необязательно)"
                            value={newDesc}
                            onChange={(e) => setNewDesc(e.target.value)}
                            style={{ flex: 1, padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
                        />
                        <button type="submit" style={{ background: '#2563eb', color: '#fff', border: 'none' }}>
                            Добавить
                        </button>
                    </div>
                </form>
            )}

            {/* Список предметов */}
            {subjects.length === 0 ? (
                <p style={{ color: '#666' }}>Пока нет предметов</p>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {subjects.map((subject) => (
                        <div
                            key={subject.id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '12px 16px',
                                background: '#fff',
                                borderRadius: 8,
                                border: '1px solid #e5e7eb',
                            }}
                        >
                            <Link
                                to={`/subjects/${subject.id}`}
                                style={{ flex: 1, textDecoration: 'none', color: '#333' }}
                            >
                                <strong>{subject.name}</strong>
                                {subject.description && (
                                    <span style={{ color: '#666', marginLeft: 10, fontSize: 14 }}>
                                        — {subject.description}
                                    </span>
                                )}
                            </Link>

                            {/* Кнопка удаления (только для админа) */}
                            {isAdmin && (
                                <button
                                    onClick={() => handleDelete(subject.id, subject.name)}
                                    style={{
                                        background: '#fee2e2',
                                        color: '#dc2626',
                                        border: 'none',
                                        padding: '4px 12px',
                                        borderRadius: 4,
                                        fontSize: 13,
                                    }}
                                >
                                    Удалить
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

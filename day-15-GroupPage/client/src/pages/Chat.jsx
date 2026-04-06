import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';

export default function Chat() {
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [text, setText] = useState('');
    const [error, setError] = useState('');
    const messagesEndRef = useRef(null);

    // Загружаем сообщения при открытии
    useEffect(() => {
        loadMessages();
    }, []);

    // Polling: каждые 3 секунды проверяем новые сообщения
    useEffect(() => {
        const interval = setInterval(loadMessages, 3000);
        return () => clearInterval(interval); // Очищаем при размонтировании
    }, []);

    // Авто-скролл вниз при новых сообщениях
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadMessages = async () => {
        try {
            const res = await api.get('/api/messages');
            setMessages(res.data.messages);
        } catch (err) {
            // Тихо игнорируем ошибки polling — не спамим пользователя
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!text.trim()) return;

        try {
            await api.post('/api/messages', { text });
            setText(''); // Очищаем поле
            loadMessages(); // Сразу обновляем список
        } catch (err) {
            setError(err.response?.data?.error || 'Ошибка отправки');
        }
    };

    // Форматируем время сообщения
    const formatTime = (dateStr) => {
        const d = new Date(dateStr);
        return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 60px)' }}>
            <h2 style={{ marginBottom: 15 }}>Чат группы</h2>

            {error && (
                <div style={{
                    background: '#fee2e2',
                    color: '#dc2626',
                    padding: '8px 12px',
                    borderRadius: 6,
                    marginBottom: 10,
                    fontSize: 14,
                }}>
                    {error}
                </div>
            )}

            {/* Список сообщений */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                background: '#f9fafb',
                borderRadius: 8,
                padding: 15,
                marginBottom: 15,
                border: '1px solid #e5e7eb',
            }}>
                {messages.length === 0 ? (
                    <p style={{ color: '#999', textAlign: 'center', marginTop: 40 }}>
                        Пока нет сообщений. Напишите первое!
                    </p>
                ) : (
                    messages.map((msg) => {
                        const isMine = msg.user_id === user?.id;
                        return (
                            <div
                                key={msg.id}
                                style={{
                                    display: 'flex',
                                    justifyContent: isMine ? 'flex-end' : 'flex-start',
                                    marginBottom: 8,
                                }}
                            >
                                <div style={{
                                    maxWidth: '70%',
                                    padding: '8px 12px',
                                    borderRadius: 12,
                                    background: isMine ? '#2563eb' : '#fff',
                                    color: isMine ? '#fff' : '#333',
                                    border: isMine ? 'none' : '1px solid #e5e7eb',
                                }}>
                                    {!isMine && (
                                        <div style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 2, color: '#666' }}>
                                            {msg.username}
                                        </div>
                                    )}
                                    <div style={{ fontSize: 14 }}>{msg.text}</div>
                                    <div style={{
                                        fontSize: 11,
                                        marginTop: 3,
                                        textAlign: 'right',
                                        opacity: 0.7,
                                    }}>
                                        {formatTime(msg.created_at)}
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Форма отправки */}
            <form onSubmit={handleSend} style={{ display: 'flex', gap: 10 }}>
                <input
                    type="text"
                    placeholder="Написать сообщение..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    style={{
                        flex: 1,
                        padding: '10px 14px',
                        border: '1px solid #ddd',
                        borderRadius: 8,
                        fontSize: 14,
                    }}
                />
                <button
                    type="submit"
                    style={{
                        background: '#2563eb',
                        color: '#fff',
                        border: 'none',
                        padding: '10px 20px',
                        borderRadius: 8,
                        fontSize: 14,
                    }}
                >
                    Отправить
                </button>
            </form>
        </div>
    );
}

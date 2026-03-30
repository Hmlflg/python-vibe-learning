from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database.models import MoodEntry


def add_mood_entry(
    db: Session,
    user_id: int,
    mood_emoji: str,
    tags: str | None = None,
    comment: str | None = None,
):
    """Добавляет новую запись настроения"""
    entry = MoodEntry(
        user_id=user_id,
        mood_emoji=mood_emoji,
        tags=tags,
        comment=comment,
        timestamp=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_user_entries(db: Session, user_id: int, limit: int = 50):
    """Получает все записи пользователя"""
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .order_by(MoodEntry.timestamp.desc())
        .limit(limit)
        .all()
    )


def get_entries_by_period(db: Session, user_id: int, days: int = 30):
    """Получает записи за последние N дней"""
    start_date = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .filter(MoodEntry.timestamp >= start_date)
        .order_by(MoodEntry.timestamp.desc())
        .all()
    )


def get_mood_statistics(db: Session, user_id: int):
    """Простая статистика по настроению пользователя"""
    entries = get_user_entries(db, user_id, limit=1000)

    if not entries:
        return {"total": 0, "moods": {}, "avg_per_day": 0}

    total = len(entries)
    mood_count = {}

    for entry in entries:
        emoji = entry.mood_emoji
        mood_count[emoji] = mood_count.get(emoji, 0) + 1

    return {
        "total": total,
        "moods": mood_count,
        "avg_per_day": round(total / 30, 1) if total > 0 else 0,  # примерно за месяц
    }

from datetime import datetime, timedelta

from database.models import MoodEntry
from sqlalchemy.orm import Session


def add_mood_entry(
    db: Session,
    user_id: int,
    mood_emoji: str,
    comment: str | None = None,
):
    """Добавляет новую запись настроения"""
    entry = MoodEntry(
        user_id=user_id,
        mood_emoji=mood_emoji,
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


def get_mood_statistics(db: Session, user_id: int, period: str = "all"):
    """Статистика по настроению пользователя с периодами"""
    now = datetime.utcnow()
    
    if period == "week":
        entries = get_entries_by_period(db, user_id, days=7)
        days_count = 7
    elif period == "month":
        entries = get_entries_by_period(db, user_id, days=30)
        days_count = 30
    else:  # "all"
        entries = get_user_entries(db, user_id, limit=1000)
        days_count = 30  # по умолчанию
    
    if not entries:
        return {
            "total": 0,
            "moods": {},
            "avg_per_day": 0,
            "period": period,
            "streak": 0,
        }
    
    total = len(entries)
    mood_count = {}
    
    for entry in entries:
        emoji = entry.mood_emoji
        mood_count[emoji] = mood_count.get(emoji, 0) + 1
    
    # Расчёт процентов
    mood_stats = {}
    for emoji, count in mood_count.items():
        percent = round((count / total) * 100)
        mood_stats[emoji] = {"count": count, "percent": percent}
    
    # Расчёт серии дней (streak)
    streak = calculate_streak(entries)
    
    return {
        "total": total,
        "moods": mood_stats,
        "avg_per_day": round(total / days_count, 1),
        "period": period,
        "streak": streak,
    }


def calculate_streak(entries) -> int:
    """Вычисляет текущую серию дней подряд с записями"""
    if not entries:
        return 0
    
    today = datetime.utcnow().date()
    dates = sorted(set(e.timestamp.date() for e in entries), reverse=True)
    
    streak = 0
    expected_date = today
    
    for date in dates:
        if date == expected_date:
            streak += 1
            expected_date = date - timedelta(days=1)
        elif date == today - timedelta(days=1):
            # Вчерашний день - серия продолжается
            streak = 1
            expected_date = date - timedelta(days=1)
        else:
            break
    
    return streak

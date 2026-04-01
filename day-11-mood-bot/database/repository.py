from datetime import UTC, datetime, timedelta

from database.models import MoodEntry
from sqlalchemy.orm import Session

MOOD_EMOJI_BY_KEY = {
    "excellent": "😊",
    "good": "🙂",
    "normal": "😐",
    "bad": "😔",
    "awful": "😢",
}

MOOD_KEY_BY_EMOJI = {emoji: key for key, emoji in MOOD_EMOJI_BY_KEY.items()}

MOOD_SCORES = {
    "excellent": 5,
    "good": 4,
    "normal": 3,
    "bad": 2,
    "awful": 1,
}


def utc_now() -> datetime:
    """Возвращает текущее UTC-время без timezone в формате, совместимом с SQLite."""
    return datetime.now(UTC).replace(tzinfo=None)


def normalize_mood_key(
    mood_key: str | None = None, mood_emoji: str | None = None
) -> str:
    """Нормализует состояние в текстовый ключ."""
    if mood_key:
        return mood_key
    if mood_emoji:
        return MOOD_KEY_BY_EMOJI.get(mood_emoji, "normal")
    return "normal"


def get_entry_mood_key(entry: MoodEntry) -> str:
    """Возвращает текстовый ключ состояния из записи с поддержкой legacy-данных."""
    mood_key = getattr(entry, "mood_key", None)
    mood_emoji = getattr(entry, "mood_emoji", None)
    return normalize_mood_key(mood_key, mood_emoji)


def get_mood_emoji(mood_key: str) -> str:
    """Возвращает emoji для текстового ключа состояния."""
    return MOOD_EMOJI_BY_KEY.get(mood_key, "😐")


def add_mood_entry(
    db: Session,
    user_id: int,
    mood_key: str,
    reason: str | None = None,
    comment: str | None = None,
):
    """Добавляет новую запись состояния."""
    entry = MoodEntry(
        user_id=user_id,
        mood_key=mood_key,
        mood_emoji=get_mood_emoji(mood_key),
        reason=reason,
        comment=comment,
        timestamp=utc_now(),
    )
    db.add(entry)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
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


def get_all_user_entries(db: Session, user_id: int):
    """Получает все записи пользователя без ограничения."""
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .order_by(MoodEntry.timestamp.desc())
        .all()
    )


def get_entries_by_period(db: Session, user_id: int, days: int = 30):
    """Получает записи за последние N дней"""
    start_date = utc_now() - timedelta(days=days)
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .filter(MoodEntry.timestamp >= start_date)
        .order_by(MoodEntry.timestamp.desc())
        .all()
    )


def get_entries_for_date(db: Session, user_id: int, target_date):
    """Получает записи пользователя за конкретную дату."""
    start_date = datetime.combine(target_date, datetime.min.time())
    end_date = start_date + timedelta(days=1)
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .filter(MoodEntry.timestamp >= start_date)
        .filter(MoodEntry.timestamp < end_date)
        .order_by(MoodEntry.timestamp.desc())
        .all()
    )


def get_latest_entry_for_day(db: Session, user_id: int, target_date):
    """Возвращает последнюю запись пользователя за указанную дату."""
    start_date = datetime.combine(target_date, datetime.min.time())
    end_date = start_date + timedelta(days=1)
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .filter(MoodEntry.timestamp >= start_date)
        .filter(MoodEntry.timestamp < end_date)
        .order_by(MoodEntry.timestamp.desc())
        .first()
    )


def update_mood_entry(
    db: Session,
    entry: MoodEntry,
    mood_key: str,
    reason: str | None = None,
    comment: str | None = None,
):
    """Обновляет существующую запись состояния."""
    entry.mood_key = mood_key
    entry.mood_emoji = get_mood_emoji(mood_key)
    entry.reason = reason
    entry.comment = comment
    entry.timestamp = utc_now()
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(entry)
    return entry


def get_entries_for_month(db: Session, user_id: int, year: int, month: int):
    """Получает записи пользователя за конкретный месяц."""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user_id)
        .filter(MoodEntry.timestamp >= start_date)
        .filter(MoodEntry.timestamp < end_date)
        .order_by(MoodEntry.timestamp.desc())
        .all()
    )


def get_mood_statistics(db: Session, user_id: int, period: str = "all"):
    """Возвращает статистику состояний пользователя по периодам."""
    now = utc_now()

    if period == "day":
        entries = get_entries_for_date(db, user_id, now.date())
        days_count = 1
        period_start = now.date()
    elif period == "week":
        entries = get_entries_by_period(db, user_id, days=7)
        days_count = 7
        period_start = (now - timedelta(days=6)).date()
    elif period == "month":
        entries = get_entries_by_period(db, user_id, days=30)
        days_count = 30
        period_start = (now - timedelta(days=29)).date()
    else:  # "all"
        entries = (
            db.query(MoodEntry)
            .filter(MoodEntry.user_id == user_id)
            .order_by(MoodEntry.timestamp.desc())
            .all()
        )
        days_count = 1
        period_start = entries[-1].timestamp.date() if entries else now.date()

    if not entries:
        return {
            "total": 0,
            "moods": {},
            "reasons": {},
            "avg_per_day": 0,
            "period": period,
            "streak": 0,
            "active_days": 0,
            "dominant_mood": None,
            "latest_entry": None,
            "tracking_days": 0,
            "best_day": None,
            "worst_day": None,
            "top_reasons": [],
            "negative_reasons": [],
            "positive_reasons": [],
        }

    if period == "all":
        oldest_entry = entries[-1].timestamp.date()
        newest_entry = entries[0].timestamp.date()
        days_count = max((newest_entry - oldest_entry).days + 1, 1)
        period_start = oldest_entry

    total = len(entries)
    mood_count = {}
    reason_count = {}
    negative_reason_count = {}
    positive_reason_count = {}
    day_scores = {}
    unique_days = set()

    for entry in entries:
        mood_key = get_entry_mood_key(entry)
        mood_count[mood_key] = mood_count.get(mood_key, 0) + 1
        reason = entry.reason or "none"
        reason_count[reason] = reason_count.get(reason, 0) + 1

        score = MOOD_SCORES.get(mood_key, 3)
        if score <= 2:
            negative_reason_count[reason] = negative_reason_count.get(reason, 0) + 1
        elif score >= 4:
            positive_reason_count[reason] = positive_reason_count.get(reason, 0) + 1

        entry_day = entry.timestamp.date()
        unique_days.add(entry_day)
        day_scores.setdefault(entry_day, []).append(score)

    # Расчёт процентов
    mood_stats = {}
    for mood_key, count in mood_count.items():
        percent = round((count / total) * 100)
        mood_stats[mood_key] = {"count": count, "percent": percent}

    reason_stats = {}
    for reason, count in reason_count.items():
        percent = round((count / total) * 100)
        reason_stats[reason] = {"count": count, "percent": percent}

    # Расчёт серии дней (streak)
    streak = calculate_streak(entries)

    dominant_key, dominant_count = max(
        mood_count.items(), key=lambda item: (item[1], MOOD_SCORES.get(item[0], 0))
    )
    dominant_mood = {
        "key": dominant_key,
        "count": dominant_count,
        "percent": mood_stats[dominant_key]["percent"],
    }

    latest_entry = entries[0]
    best_day = None
    worst_day = None
    if len(day_scores) > 1:
        day_averages = {
            day: sum(scores) / len(scores) for day, scores in day_scores.items()
        }
        best_day_date = max(day_averages, key=lambda day: day_averages[day])
        worst_day_date = min(day_averages, key=lambda day: day_averages[day])
        best_day = {
            "date": best_day_date,
            "score": round(day_averages[best_day_date], 1),
        }
        worst_day = {
            "date": worst_day_date,
            "score": round(day_averages[worst_day_date], 1),
        }

    top_reasons = sorted(
        reason_stats.items(),
        key=lambda item: (item[1]["count"], item[1]["percent"]),
        reverse=True,
    )[:3]
    negative_reasons = sorted(
        negative_reason_count.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    positive_reasons = sorted(
        positive_reason_count.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]

    return {
        "total": total,
        "moods": mood_stats,
        "reasons": reason_stats,
        "avg_per_day": round(total / days_count, 1),
        "period": period,
        "streak": streak,
        "active_days": len(unique_days),
        "dominant_mood": dominant_mood,
        "latest_entry": latest_entry,
        "tracking_days": max((now.date() - period_start).days + 1, 1),
        "best_day": best_day,
        "worst_day": worst_day,
        "top_reasons": top_reasons,
        "negative_reasons": negative_reasons,
        "positive_reasons": positive_reasons,
    }


def calculate_streak(entries) -> int:
    """Вычисляет текущую серию дней подряд с записями"""
    if not entries:
        return 0

    today = utc_now().date()
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

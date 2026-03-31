from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MoodEntry(Base):
    """Модель записи состояния в базе данных."""

    __tablename__ = "mood_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Основная оценка состояния через эмодзи
    mood_emoji: Mapped[str] = mapped_column(String(10), nullable=False)

    # Комментарий пользователя
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


# Эта функция будет вызвана один раз при первом запуске
def create_tables(engine):
    Base.metadata.create_all(bind=engine)

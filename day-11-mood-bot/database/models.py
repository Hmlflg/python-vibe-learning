from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MoodEntry(Base):
    """Модель записи настроения в базе данных"""

    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Основная оценка настроения (эмодзи)
    mood_emoji = Column(String(10), nullable=False)

    # Теги эмоций (храним как строку через запятую, например: "Радость,Энергия")
    tags = Column(Text, nullable=True)

    # Комментарий пользователя
    comment = Column(Text, nullable=True)


# Эта функция будет вызвана один раз при первом запуске
def create_tables(engine):
    Base.metadata.create_all(bind=engine)

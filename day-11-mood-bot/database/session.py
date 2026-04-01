from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from database.models import create_tables

# Путь к базе данных
DATABASE_URL = "sqlite:///./mood.db"

# Создаём движок
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаём таблицы при импорте (если их ещё нет)
try:
    create_tables(engine)
except OperationalError:
    pass


def ensure_schema():
    """Добавляет недостающие колонки в существующую SQLite-схему."""
    try:
        inspector = inspect(engine)
        columns = {column["name"] for column in inspector.get_columns("mood_entries")}

        with engine.begin() as connection:
            if "mood_key" not in columns:
                connection.execute(
                    text("ALTER TABLE mood_entries ADD COLUMN mood_key VARCHAR(20)")
                )
            if "reason" not in columns:
                connection.execute(
                    text("ALTER TABLE mood_entries ADD COLUMN reason VARCHAR(50)")
                )
            if "mood_key" in columns or "mood_key" not in columns:
                connection.execute(
                    text(
                        """
                        UPDATE mood_entries
                        SET mood_key = CASE mood_emoji
                            WHEN '😊' THEN 'excellent'
                            WHEN '🙂' THEN 'good'
                            WHEN '😐' THEN 'normal'
                            WHEN '😔' THEN 'bad'
                            WHEN '😢' THEN 'awful'
                            ELSE mood_key
                        END
                        WHERE mood_key IS NULL OR mood_key = ''
                        """
                    )
                )
    except OperationalError:
        # Если файл SQLite сейчас недоступен, не валим импорт приложения.
        pass


ensure_schema()


def create_session():
    """Возвращает новую сессию базы данных."""
    return SessionLocal()


def get_db():
    """Генератор для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

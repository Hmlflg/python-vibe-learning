from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
create_tables(engine)


def get_db():
    """Генератор для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

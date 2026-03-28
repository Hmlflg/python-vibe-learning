from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаём движок базы данных (файл expenses.db)
DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ExpenseDB(Base):
    """Модель расхода в базе данных"""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    category = Column(String, index=True)
    amount = Column(Float)
    description = Column(String, nullable=True)


# Создаём таблицы при первом запуске
Base.metadata.create_all(bind=engine)


def get_db():
    """Генератор сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

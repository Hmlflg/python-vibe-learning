from datetime import datetime

from database import ExpenseDB
from sqlalchemy.orm import Session


def add_expense(db: Session, category: str, amount: float, description: str = ""):
    """Добавляет новый расход в базу"""
    db_expense = ExpenseDB(
        category=category, amount=amount, description=description, date=datetime.now()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_all_expenses(db: Session, limit: int = 50):
    """Получает все расходы (с лимитом)"""
    return db.query(ExpenseDB).order_by(ExpenseDB.date.desc()).limit(limit).all()


def get_expenses_by_category(db: Session, category: str):
    """Получает расходы по категории"""
    return db.query(ExpenseDB).filter(ExpenseDB.category.ilike(f"%{category}%")).all()


def get_statistics(db: Session):
    """Возвращает базовую статистику по расходам"""
    expenses = db.query(ExpenseDB).all()

    if not expenses:
        return {"total": 0.0, "count": 0, "avg": 0.0, "categories": {}}

    total = 0.0
    categories = {}

    for exp in expenses:
        # Явно извлекаем значения из объекта
        amount = float(getattr(exp, "amount", 0))
        category_str = str(getattr(exp, "category", "")).strip()

        cat = category_str.capitalize() if category_str else "Без категории"

        total += amount
        categories[cat] = categories.get(cat, 0.0) + amount

    count = len(expenses)
    avg = round(total / count, 2) if count > 0 else 0.0

    return {
        "total": round(total, 2),
        "count": count,
        "avg": avg,
        "categories": categories,
    }

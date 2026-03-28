import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("expenses.json")


def load_expenses() -> list[dict]:
    """Загружает все расходы"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_expenses(expenses: list[dict]) -> None:
    """Сохраняет расходы"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)


def add_expense(category: str, amount: float, description: str = ""):
    """Добавляет новый расход"""
    expenses = load_expenses()

    new_expense = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "category": category,
        "amount": amount,
        "description": description,
    }

    expenses.append(new_expense)
    save_expenses(expenses)
    return new_expense

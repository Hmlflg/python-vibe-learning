import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Expense, ExpenseCreate

app = FastAPI(
    title="Expense API",
    description="API для управления личными расходами",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path("expenses.json")


def load_expenses() -> list[dict]:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_expenses(expenses: list[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=4, ensure_ascii=False)


@app.get("/")
def root():
    return {"message": "Expense API работает! 🚀 Перейди на /docs"}


@app.get("/expenses", response_model=List[Expense])
def get_all_expenses():
    """Получить все расходы"""
    expenses = load_expenses()
    for i, exp in enumerate(expenses, 1):
        if "id" not in exp:
            exp["id"] = i
    return expenses


@app.post("/expenses", response_model=Expense)
def create_expense(expense: ExpenseCreate):
    """Добавить новый расход"""
    expenses = load_expenses()

    new_expense = expense.dict()
    new_expense["id"] = len(expenses) + 1

    expenses.append(new_expense)
    save_expenses(expenses)

    print(
        f"✅ Добавлен: {new_expense['description']} ({new_expense['category']}) — {new_expense['amount']} руб."
    )
    return new_expense


@app.get("/expenses/category/{category}", response_model=List[Expense])
def get_expenses_by_category(category: str):
    """Получить расходы по категории"""
    expenses = load_expenses()
    filtered = [
        exp
        for exp in expenses
        if str(exp.get("category", "")).strip().lower() == category.strip().lower()
    ]
    for i, exp in enumerate(filtered, 1):
        if "id" not in exp:
            exp["id"] = i
    return filtered


@app.get("/statistics")
def get_statistics():
    """Получить статистику по расходам"""
    expenses = load_expenses()

    if not expenses:
        return {"message": "Нет расходов для анализа"}

    total_amount = sum(exp.get("amount", 0) for exp in expenses)
    count = len(expenses)
    avg_amount = round(total_amount / count, 2) if count > 0 else 0

    # Расходы по категориям
    by_category = defaultdict(float)
    for exp in expenses:
        cat = exp.get("category", "Прочее")
        by_category[cat] += exp.get("amount", 0)

    # Топ-3 самых дорогих расхода
    top_expenses = sorted(expenses, key=lambda x: x.get("amount", 0), reverse=True)[:3]

    return {
        "total_expenses": count,
        "total_amount": round(total_amount, 2),
        "average_amount": avg_amount,
        "categories": dict(by_category),
        "top_expenses": [
            {
                "description": exp.get("description"),
                "amount": exp.get("amount"),
                "category": exp.get("category"),
            }
            for exp in top_expenses
        ],
    }


# Создаём тестовые данные при первом запуске
if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
    test_expenses = [
        {
            "description": "Обед в кафе",
            "amount": 850.5,
            "category": "Еда",
            "date": "2026-03-25",
        },
        {
            "description": "Проезд на метро",
            "amount": 80.0,
            "category": "Транспорт",
            "date": "2026-03-24",
        },
        {
            "description": "Кофе навынос",
            "amount": 250.0,
            "category": "Еда",
            "date": "2026-03-26",
        },
        {
            "description": "Подписка на YouTube Premium",
            "amount": 799.0,
            "category": "Развлечения",
            "date": "2026-03-20",
        },
        {
            "description": "Продукты в Пятёрочке",
            "amount": 1240.75,
            "category": "Еда",
            "date": "2026-03-27",
        },
    ]
    save_expenses(test_expenses)
    print("✅ Создано 5 тестовых расходов")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

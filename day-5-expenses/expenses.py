import json
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_FILE = Path("expenses.json")


def load_expenses() -> list[dict]:
    """Загружает расходы из JSON файла или возвращает пустой список."""
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_expenses(expenses: list[dict]) -> None:
    """Сохраняет список расходов в JSON файл с красивым форматированием."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4, ensure_ascii=False)


def add_expense() -> dict:
    """Спрашивает у пользователя данные о расходе и возвращает новую запись."""
    description = input("📝 Описание: ").strip()

    while True:
        try:
            amount = float(input("💵 Сумма: "))
            if amount <= 0:
                print("⚠️  Сумма должна быть больше 0!")
                continue
            break
        except ValueError:
            print("⚠️  Введите корректное число!")

    category = (
        input("🏷️  Категория (еда/транспорт/развлечения/прочее): ").strip() or "прочее"
    )
    date = input(
        "📅 Дата (YYYY-MM-DD) [по умолчанию сегодня]: "
    ).strip() or datetime.now().strftime("%Y-%m-%d")

    return {
        "description": description,
        "amount": amount,
        "category": category,
        "date": date,
    }


def show_expenses(expenses: list[dict]) -> None:
    """Красиво выводит все расходы с нумерацией."""
    if not expenses:
        print("\n📭 Нет расходов. Список пуст!\n")
        return

    print("\n" + "=" * 70)
    print(f"{'#':<3} {'Дата':<12} {'Категория':<15} {'Описание':<20} {'Сумма':>10}")
    print("=" * 70)

    total = 0
    for i, expense in enumerate(expenses, 1):
        date = expense.get("date", "N/A")
        category = expense.get("category", "N/A")
        description = expense.get("description", "N/A")[:18]  # Truncate if too long
        amount = expense.get("amount", 0)

        print(f"{i:<3} {date:<12} {category:<15} {description:<20} {amount:>10.2f}")
        total += amount

    print("=" * 70)
    print(f"{'Всего:':<50} {total:>10.2f}")
    print("=" * 70 + "\n")


def show_statistics(expenses: list[dict]) -> None:
    """Показывает статистику по расходам: сумму, среднее, топ-3 и по категориям."""
    if not expenses:
        print("\n📭 Нет расходов для анализа!\n")
        return

    # Общая сумма и среднее
    total = sum(e.get("amount", 0) for e in expenses)
    average = total / len(expenses)

    print("\n" + "=" * 70)
    print("📊 СТАТИСТИКА РАСХОДОВ")
    print("=" * 70)
    print(f"💰 Общая сумма:      {total:>10.2f}")
    print(f"📈 Средний расход:   {average:>10.2f}")
    print(f"📋 Количество:       {len(expenses):>10}")

    # Топ-3 расхода
    print("\n🔝 ТОП-3 РАСХОДА:")
    print("-" * 70)
    for i, expense in enumerate(
        sorted(expenses, key=lambda x: x.get("amount", 0), reverse=True)[:3], 1
    ):
        desc = expense.get("description", "N/A")[:30]
        amount = expense.get("amount", 0)
        category = expense.get("category", "N/A")
        print(f"  {i}. {desc:<30} {amount:>10.2f} ({category})")

    # Расходы по категориям
    print("\n📁 РАСХОДЫ ПО КАТЕГОРИЯМ:")
    print("-" * 70)
    categories = {}
    for expense in expenses:
        cat = expense.get("category", "прочее")
        amount = expense.get("amount", 0)
        categories[cat] = categories.get(cat, 0) + amount

    for category in sorted(categories.keys()):
        amount = categories[category]
        percentage = (amount / total * 100) if total > 0 else 0
        print(f"  {category:<20} {amount:>10.2f} ({percentage:>5.1f}%)")

    print("=" * 70 + "\n")


def main():
    """Главное меню анализатора расходов."""
    print("💰 Анализатор расходов запущен\n")

    while True:
        print("=" * 70)
        print("МЕНЮ:")
        print("=" * 70)
        print("1. ➕ Добавить новый расход")
        print("2. 📋 Показать все расходы")
        print("3. 📊 Показать статистику")
        print("4. 🚪 Выход")
        print("=" * 70)

        choice = input("\nВыберите действие (1-4): ").strip()

        if choice == "1":
            expenses = load_expenses()
            new_expense = add_expense()
            expenses.append(new_expense)
            save_expenses(expenses)
            print("✅ Расход успешно добавлен!\n")

        elif choice == "2":
            expenses = load_expenses()
            show_expenses(expenses)

        elif choice == "3":
            expenses = load_expenses()
            show_statistics(expenses)

        elif choice == "4":
            print("\n👋 До свидания!\n")
            break

        else:
            print("⚠️  Некорректный ввод! Выберите 1-4\n")


if __name__ == "__main__":
    main()

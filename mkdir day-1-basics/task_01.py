from typing import Any


def greet(name: str, age: int) -> str:
    """Возвращает приветствие с именем и возрастом."""
    return f"Привет, {name}! Тебе {age} лет."


def get_even_numbers(numbers: list[int]) -> list[int]:
    """Возвращает отсортированный список только чётных чисел."""
    return sorted([n for n in numbers if n % 2 == 0])


def describe_person(person: dict[str, Any]) -> str:
    """Возвращает красивое описание человека из словаря."""
    name: str = person.get("name", "Неизвестно")
    age: int = person.get("age", 0)
    city: str = person.get("city", "Неизвестно")

    base = f"{name} живёт в {city} и ему {age} лет."

    if age < 18:
        base += " (ещё школьник!)"
    elif age >= 60:
        base += " (почтенный возраст!)"

    return base


# ───────────────────────────────────────────────────────────────
# Примеры использования
if __name__ == "__main__":
    print(greet("Алексей", 30))
    print(greet("Мария", 25))

    print(get_even_numbers([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))

    print(describe_person({"name": "Алексей", "age": 30, "city": "Москва"}))
    print(describe_person({"name": "Мария", "age": 16, "city": "Санкт-Петербург"}))
    print(describe_person({"name": "Иван", "age": 25, "city": "Екатеринбург"}))
    print(describe_person({"name": "Анна", "age": 67, "city": "Новосибирск"}))

import json
from typing import Any


def save_to_json(filename: str, data: list[dict]) -> None:
    """Сохраняет список словарей в JSON-файл с отступом 4."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_from_json(filename: str) -> list[dict]:
    """Загружает список словарей из JSON-файла с безопасной обработкой ошибок."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Возвращаю пустой список.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filename}. Возвращаю пустой список.")
        return []


def describe_person(person: dict[str, Any]) -> str:
    """Возвращает красивое описание человека из словаря."""
    name: str = person.get("name", "Неизвестно")
    age: int = person.get("age", 0)
    city: str = person.get("city", "Неизвестно")
    gender: str = person.get("gender", "m")  # m for male, f for female

    pronoun = "ему" if gender == "m" else "ей"

    base = f"{name} живёт в {city} и {pronoun} {age} лет."

    if age < 18:
        base += " (ещё школьник!)" if gender == "m" else " (ещё школьница!)"
    elif age >= 60:
        base += " (почтенный возраст!)"

    return base


if __name__ == "__main__":
    # Создаём список вымышленных пользователей
    users = [
        {
            "name": "Алексей Иванов",
            "age": 30,
            "city": "Москва",
            "profession": "Инженер",
            "gender": "m",
        },
        {
            "name": "Мария Петрова",
            "age": 25,
            "city": "Санкт-Петербург",
            "profession": "Дизайнер",
            "gender": "f",
        },
        {
            "name": "Иван Сидоров",
            "age": 35,
            "city": "Екатеринбург",
            "profession": "Программист",
            "gender": "m",
        },
        {
            "name": "Анна Кузнецова",
            "age": 28,
            "city": "Новосибирск",
            "profession": "Учитель",
            "gender": "f",
        },
        {
            "name": "Дмитрий Смирнов",
            "age": 42,
            "city": "Казань",
            "profession": "Врач",
            "gender": "m",
        },
        {
            "name": "Елена Волкова",
            "age": 31,
            "city": "Нижний Новгород",
            "profession": "Журналист",
            "gender": "f",
        },
    ]

    # Сохраняем в файл
    save_to_json("users.json", users)
    print("Пользователи сохранены в файл users.json")

    # Загружаем обратно
    loaded_users = load_from_json("users.json")

    # Выводим красиво
    print("\nЗагруженные пользователи:")
    for user in loaded_users:
        description = describe_person(user)
        print(f"{description}, работает {user['profession']}.")

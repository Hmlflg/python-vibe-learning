import json
from typing import Any


def save_to_json(filename: str, data: list[dict[str, Any]]) -> None:
    """Сохраняет список словарей в JSON-файл с красивым форматированием."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Данные успешно сохранены в {filename}")


def load_from_json(filename: str) -> list[dict[str, Any]]:
    """Загружает список словарей из JSON-файла с безопасной обработкой ошибок."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Файл {filename} не найден. Возвращаем пустой список.")
        return []
    except json.JSONDecodeError:
        print(
            f"❌ Ошибка декодирования JSON в файле {filename}. Возвращаем пустой список."
        )
        return []
    except Exception as e:  # на всякий случай
        print(f"Неизвестная ошибка при чтении {filename}: {e}")
        return []


def describe_person(person: dict[str, Any]) -> str:
    """Возвращает красивое описание человека."""
    name: str = person.get("name", "Неизвестно")
    age: int = person.get("age", 0)
    city: str = person.get("city", "Неизвестно")
    profession: str = person.get("profession", "Неизвестно")
    gender: str = person.get("gender", "m")

    pronoun = "ему" if gender == "m" else "ей"
    school_word = "школьник" if gender == "m" else "школьница"

    base = f"{name} живёт в {city} и {pronoun} {age} лет."

    if age < 18:
        base += f" (ещё {school_word}!)"
    elif age >= 60:
        base += " (почтенный возраст!)"

    return f"{base}, работает {profession}."


if __name__ == "__main__":
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

    # Сохраняем и загружаем
    save_to_json("users.json", users)
    loaded_users = load_from_json("users.json")

    print("\nЗагруженные пользователи:")
    for i, user in enumerate(loaded_users, 1):
        print(f"{i}. {describe_person(user)}")

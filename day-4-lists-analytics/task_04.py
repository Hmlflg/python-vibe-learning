import json
from pathlib import Path
from typing import Any


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


def filter_adults(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Возвращает список пользователей старше или равных 18 лет."""
    return [user for user in users if user.get("age", 0) >= 18]


def group_by_city(users: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Группирует пользователей по городу и возвращает словарь city -> [users]."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for user in users:
        city = user.get("city", "Неизвестно")
        grouped.setdefault(city, []).append(user)
    return grouped


def show_statistics(users: list[dict[str, Any]]) -> None:
    """Выводит базовую статистику по списку пользователей."""
    total = len(users)
    if total == 0:
        print("Статистика: список пользователей пуст.")
        return

    ages = [user.get("age", 0) for user in users]
    average_age = round(sum(ages) / total, 1)

    grouped = group_by_city(users)
    most_popular = max(grouped.items(), key=lambda item: len(item[1]))
    most_popular_city = most_popular[0]
    city_count = len(most_popular[1])

    adult_count = sum(1 for age in ages if age >= 18)
    minor_count = total - adult_count

    print("📊 Статистика по пользователям:")
    print(f"Всего пользователей: {total}")
    print(f"Средний возраст: {average_age} лет")
    print(f"Самый популярный город: {most_popular_city} ({city_count} человека)")
    print(f"Совершеннолетних: {adult_count}")
    print(f"Несовершеннолетних: {minor_count}")


if __name__ == "__main__":
    # Загружаем пользователей из users.json
    users = load_from_json("../day-2-files-json/users.json")

    # Если файл не найден, используем пример
    if not users:
        users = [
            {
                "name": "Алексей Иванов",
                "age": 30,
                "city": "Москва",
                "profession": "Инженер",
            },
            {
                "name": "Мария Петрова",
                "age": 25,
                "city": "Санкт-Петербург",
                "profession": "Дизайнер",
            },
            {
                "name": "Иван Сидоров",
                "age": 35,
                "city": "Екатеринбург",
                "profession": "Программист",
            },
            {
                "name": "Анна Кузнецова",
                "age": 16,
                "city": "Новосибирск",
                "profession": "Ученица",
            },
            {
                "name": "Дмитрий Смирнов",
                "age": 42,
                "city": "Казань",
                "profession": "Врач",
            },
            {
                "name": "Елена Волкова",
                "age": 31,
                "city": "Нижний Новгород",
                "profession": "Журналист",
            },
            {
                "name": "Сергей Морозов",
                "age": 17,
                "city": "Москва",
                "profession": "Студент",
            },
        ]

    print("🚀 Запуск аналитики пользователей\n")

    # Фильтрация взрослых
    adults = filter_adults(users)
    print("👨‍🦱 Взрослые пользователи:")
    for adult in adults:
        print(f"  - {adult['name']} ({adult['age']} лет)")
    print()

    # Группировка по городу
    grouped = group_by_city(users)
    print("🏙️ Группировка по городам:")
    for city, city_users in grouped.items():
        print(f"  📍 {city}: {len(city_users)} человек")
        for user in city_users:
            print(f"    - {user['name']}")
    print()

    # Статистика
    show_statistics(users)

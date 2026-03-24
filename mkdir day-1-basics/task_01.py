# Напиши функцию, которая принимает имя и возраст человека
# и возвращает строку вида: "Привет, [имя]! Тебе [возраст] лет."
# Используй f-строки и type hints
# def greet(name: str, age: int) -> str:
#     return f"Привет, {name}! Тебе {age} лет."


# # Пример использования функции
# print(greet("Алексей", 30))
# print(greet("Мария", 25))
# print(greet("Иван", 40))


# # Функция принимает список чисел
# # Возвращает новый список только с чётными числами, отсортированный по возрастанию
# # type hints + list comprehension
# from typing import List


# def get_even_numbers(numbers: List[int]) -> List[int]:
#     return sorted([n for n in numbers if n % 2 == 0])


# # Пример использования функции
# print(get_even_numbers([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))


# Функция принимает словарь с данными о человеке: {"name": "...", "age": ..., "city": "..."}
# Возвращает красивое предложение:
# "[name] живёт в [city] и ему/ей [age] лет."
# Если age < 18 — добавить " (ещё школьник!)"
# Используй .get() для безопасного доступа к ключам

# from typing import Dict, Union


# def describe_person(person: Dict[str, Union[str, int]]) -> str:
#     name = person.get("name", "Неизвестно")
#     age = person.get("age", 0)
#     city = person.get("city", "Неизвестно")

#     base = f"{name} живёт в {city} и ему/ей {age} лет."
#     if age < 18:
#         base += " (ещё школьник!)"
#     return base


# # Пример использования функции
# print(describe_person({"name": "Алексей", "age": 30, "city": "Москва"}))
# print(describe_person({"name": "Мария", "age": 16, "city": "Санкт-Петербург"}))
# print(describe_person({"name": "Иван", "age": 25, "city": "Екатеринбург"}))

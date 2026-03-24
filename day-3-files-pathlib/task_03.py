from datetime import datetime
from pathlib import Path


def sanitize_filename(title: str) -> str:
    """Делает из заголовка безопасное имя файла."""
    # Заменяем опасные символы на подчёркивания
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, "_")
    return title.strip().replace(" ", "_")


def write_note(title: str, text: str) -> None:
    """Создаёт папку notes и сохраняет заметку с заголовком и датой."""
    notes_dir = Path("notes")
    notes_dir.mkdir(exist_ok=True)

    safe_title = sanitize_filename(title)
    note_path = notes_dir / f"{safe_title}.txt"

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"Заголовок: {title}\n"
    content += f"Дата: {current_time}\n"
    content += f"{'-' * 40}\n\n"
    content += text

    note_path.write_text(content, encoding="utf-8")
    print(f"✅ Заметка сохранена: notes/{safe_title}.txt")


def read_note(title: str) -> str:
    """Читает заметку по заголовку."""
    notes_dir = Path("notes")
    safe_title = sanitize_filename(title)
    note_path = notes_dir / f"{safe_title}.txt"

    if not note_path.exists():
        return f"❌ Файл не найден: {note_path}"

    return note_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    print("📔 Простой дневник заметок\n")

    title = input("📝 Введите заголовок заметки: ").strip()
    while not title:
        print("❌ Заголовок не может быть пустым!")
        title = input("📝 Введите заголовок заметки: ").strip()

    text = input("✍️ Введите текст заметки:\n")

    write_note(title, text)

    print("\n📖 Содержимое сохранённой заметки:")
    content = read_note(title)
    print(content)

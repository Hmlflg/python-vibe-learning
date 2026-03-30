from aiogram.fsm.state import State, StatesGroup


class MoodStates(StatesGroup):
    """Состояния для процесса записи настроения"""

    waiting_for_mood = State()  # ожидание выбора эмодзи
    waiting_for_tags = State()  # ожидание выбора тегов
    waiting_for_comment = State()  # ожидание комментария

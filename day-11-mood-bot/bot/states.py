from aiogram.fsm.state import State, StatesGroup


class MoodStates(StatesGroup):
    """Состояния для процесса записи состояния"""

    waiting_for_mood = State()  # ожидание выбора эмодзи
    waiting_for_reason = State()  # ожидание выбора причины
    waiting_for_comment = State()  # ожидание комментария
    waiting_for_confirm = State()  # ожидание подтверждения


class StatsStates(StatesGroup):
    """Состояния для просмотра статистики"""

    viewing_stats = State()  # просмотр статистики с выбором периода

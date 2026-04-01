from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import date
from html import escape
from pathlib import Path

from database.repository import get_entry_mood_key, get_mood_emoji

MOOD_NAMES = {
    "excellent": "Отлично",
    "good": "Хорошо",
    "normal": "Нормально",
    "bad": "Плохо",
    "awful": "Ужасно",
}

REASON_NAMES = {
    "family": "Семья",
    "friends": "Друзья",
    "relationships": "Отношения",
    "work": "Работа",
    "health": "Здоровье",
    "weather": "Погода",
    "sleep": "Сон",
    "money": "Деньги",
    "study": "Учёба",
    "emotions": "Эмоции",
    "other": "Другое",
    "none": "Без причины",
}

MONTH_NAMES = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]


def format_human_date(value: date) -> str:
    return f"{value.day} {MONTH_NAMES[value.month - 1]} {value.year}"


def build_bar(percent: int) -> str:
    filled = max(1, round(percent / 10)) if percent > 0 else 0
    return "█" * filled + "░" * (10 - filled)


def _render_reason_list(items: list[tuple[str, int]], empty_text: str) -> str:
    if not items:
        return f"<p class='muted'>{escape(empty_text)}</p>"

    lines = []
    for reason_key, count in items:
        label = REASON_NAMES.get(reason_key, reason_key)
        lines.append(
            f"<li><span>{escape(label)}</span><strong>{count}</strong></li>"
        )
    return "<ul class='reason-list'>" + "".join(lines) + "</ul>"


def _render_recent_entries(entries: list) -> str:
    if not entries:
        return "<p class='muted'>Записей пока нет.</p>"

    cards = []
    for entry in entries[:10]:
        mood_key = get_entry_mood_key(entry)
        mood_label = MOOD_NAMES.get(mood_key, mood_key)
        mood_emoji = get_mood_emoji(mood_key)
        reason_label = REASON_NAMES.get(entry.reason or "none", "Без причины")
        comment = escape(entry.comment.strip()) if entry.comment else "—"
        cards.append(
            "<article class='entry-card'>"
            f"<div class='entry-head'><strong>{entry.timestamp.strftime('%d.%m.%Y %H:%M')}</strong>"
            f"<span>{mood_emoji} {escape(mood_label)}</span></div>"
            f"<div class='entry-meta'>Причина: {escape(reason_label)}</div>"
            f"<div class='entry-comment'>{comment}</div>"
            "</article>"
        )
    return "".join(cards)


def build_html_report(
    *,
    title: str,
    period_label: str,
    stats: dict,
    entries: list,
) -> str:
    total = stats.get("total", 0)
    active_days = stats.get("active_days", 0)
    streak = stats.get("streak", 0)
    tracking_days = stats.get("tracking_days", 0)
    dominant = stats.get("dominant_mood")
    dominant_text = "Пока недостаточно данных"
    if dominant:
        mood_key = dominant["key"]
        dominant_text = f"{get_mood_emoji(mood_key)} {MOOD_NAMES.get(mood_key, mood_key)}"

    mood_rows = []
    for mood_key, payload in sorted(
        stats.get("moods", {}).items(),
        key=lambda item: (item[1]["count"], item[1]["percent"]),
        reverse=True,
    ):
        mood_rows.append(
            "<div class='mood-row'>"
            f"<span class='mood-name'>{get_mood_emoji(mood_key)} {escape(MOOD_NAMES.get(mood_key, mood_key))}</span>"
            f"<span class='mood-bar'>{build_bar(payload['percent'])}</span>"
            f"<span class='mood-value'>{payload['count']} · {payload['percent']}%</span>"
            "</div>"
        )

    latest_entry = stats.get("latest_entry")
    latest_block = "<p class='muted'>Нет записей за выбранный период.</p>"
    if latest_entry is not None:
        latest_key = get_entry_mood_key(latest_entry)
        latest_reason = REASON_NAMES.get(latest_entry.reason or "none", "Без причины")
        latest_comment = escape(latest_entry.comment.strip()) if latest_entry.comment else "—"
        latest_block = (
            "<article class='latest-card'>"
            f"<div class='latest-title'>{latest_entry.timestamp.strftime('%d.%m.%Y %H:%M')}</div>"
            f"<div class='latest-state'>{get_mood_emoji(latest_key)} {escape(MOOD_NAMES.get(latest_key, latest_key))}</div>"
            f"<div class='latest-meta'>Причина: {escape(latest_reason)}</div>"
            f"<div class='latest-comment'>{latest_comment}</div>"
            "</article>"
        )

    best_day = stats.get("best_day")
    worst_day = stats.get("worst_day")
    best_day_text = "Недостаточно данных"
    if best_day:
        best_day_text = f"{format_human_date(best_day['date'])} · {best_day['score']}"
    worst_day_text = "Недостаточно данных"
    if worst_day:
        worst_day_text = f"{format_human_date(worst_day['date'])} · {worst_day['score']}"

    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f1e8;
      --panel: #fffdf8;
      --text: #1e1f1c;
      --muted: #6f7266;
      --accent: #216869;
      --accent-soft: #d8ece8;
      --border: #e8decd;
      --shadow: 0 14px 40px rgba(41, 50, 38, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Trebuchet MS", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(33, 104, 105, 0.12), transparent 32%),
        radial-gradient(circle at top right, rgba(216, 166, 113, 0.15), transparent 28%),
        linear-gradient(180deg, #f9f4eb 0%, #f4efe6 100%);
    }}
    .page {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(33, 104, 105, 0.94), rgba(81, 137, 128, 0.92));
      color: white;
      border-radius: 28px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}
    .hero h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.1;
    }}
    .hero p {{
      margin: 0;
      color: rgba(255,255,255,0.9);
      font-size: 16px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-top: 20px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 22px;
      padding: 20px;
      box-shadow: var(--shadow);
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .metric-value {{
      font-size: 28px;
      font-weight: 700;
    }}
    .section {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
    }}
    h2 {{
      margin: 0 0 16px;
      font-size: 20px;
    }}
    .mood-row {{
      display: grid;
      grid-template-columns: 150px 1fr 86px;
      gap: 12px;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid rgba(232, 222, 205, 0.8);
    }}
    .mood-row:last-child {{ border-bottom: 0; }}
    .mood-name {{ font-weight: 600; }}
    .mood-bar {{
      font-family: Consolas, monospace;
      letter-spacing: 0.06em;
      color: var(--accent);
    }}
    .mood-value {{
      text-align: right;
      color: var(--muted);
      font-weight: 600;
    }}
    .reason-columns {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .reason-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 10px;
    }}
    .reason-list li {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      background: #faf5ed;
      border-radius: 14px;
      border: 1px solid #eee3d3;
    }}
    .muted {{ color: var(--muted); }}
    .latest-card, .entry-card {{
      background: #faf6ef;
      border: 1px solid #eee1ce;
      border-radius: 16px;
      padding: 14px 16px;
    }}
    .latest-title, .entry-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 8px;
    }}
    .latest-state {{
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .entry-meta, .latest-meta {{
      color: var(--muted);
      margin-bottom: 8px;
      font-size: 14px;
    }}
    .entry-comment, .latest-comment {{
      line-height: 1.5;
    }}
    .entries {{
      display: grid;
      gap: 12px;
    }}
    .footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}
    @media (max-width: 860px) {{
      .grid,
      .section,
      .reason-columns {{
        grid-template-columns: 1fr;
      }}
      .mood-row {{
        grid-template-columns: 1fr;
      }}
      .mood-value {{
        text-align: left;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>{escape(title)}</h1>
      <p>{escape(period_label)}</p>
    </section>

    <section class="grid">
      <article class="card">
        <div class="metric-label">Всего записей</div>
        <div class="metric-value">{total}</div>
      </article>
      <article class="card">
        <div class="metric-label">Активных дней</div>
        <div class="metric-value">{active_days}</div>
      </article>
      <article class="card">
        <div class="metric-label">Серия записей</div>
        <div class="metric-value">{streak}</div>
      </article>
      <article class="card">
        <div class="metric-label">Главный фон</div>
        <div class="metric-value">{escape(dominant_text)}</div>
      </article>
    </section>

    <section class="section">
      <article class="card">
        <h2>Состояния за период</h2>
        {"".join(mood_rows) if mood_rows else "<p class='muted'>Записей пока нет.</p>"}
      </article>
      <article class="card">
        <h2>Последняя запись</h2>
        {latest_block}
      </article>
    </section>

    <section class="reason-columns">
      <article class="card">
        <h2>Главные причины</h2>
        {_render_reason_list(
            [(reason_key, payload["count"]) for reason_key, payload in stats.get("top_reasons", [])],
            "Причины пока не выделяются.",
        )}
      </article>
      <article class="card">
        <h2>Что тянуло вниз</h2>
        {_render_reason_list(stats.get("negative_reasons", []), "Тяжёлые причины не выделились.")}
      </article>
      <article class="card">
        <h2>Что поддерживало</h2>
        {_render_reason_list(stats.get("positive_reasons", []), "Поддерживающие причины не выделились.")}
      </article>
    </section>

    <section class="section">
      <article class="card">
        <h2>Ритм периода</h2>
        <ul class="reason-list">
          <li><span>Лучший день</span><strong>{escape(best_day_text)}</strong></li>
          <li><span>Самый тяжёлый день</span><strong>{escape(worst_day_text)}</strong></li>
          <li><span>Дней в трекере</span><strong>{tracking_days}</strong></li>
        </ul>
      </article>
      <article class="card">
        <h2>Последние записи</h2>
        <div class="entries">
          {_render_recent_entries(entries)}
        </div>
      </article>
    </section>

    <div class="footer">Отчёт создан ботом отслеживания состояния.</div>
  </main>
</body>
</html>"""
    return html


def create_html_report_file(
    *,
    title: str,
    period_label: str,
    stats: dict,
    entries: list,
    filename_prefix: str,
) -> Path:
    html = build_html_report(
        title=title,
        period_label=period_label,
        stats=stats,
        entries=entries,
    )
    fd, path_str = tempfile.mkstemp(prefix=filename_prefix, suffix=".html")
    os.close(fd)
    path = Path(path_str)
    with path.open("w", encoding="utf-8") as file:
        file.write(html)
    path.chmod(0o600)
    return path


def create_csv_export_file(entries: list, filename_prefix: str) -> Path:
    fd, path_str = tempfile.mkstemp(prefix=filename_prefix, suffix=".csv")
    os.close(fd)
    path = Path(path_str)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["id", "timestamp", "state_key", "state_label", "emoji", "reason", "comment"]
        )
        for entry in entries:
            mood_key = get_entry_mood_key(entry)
            writer.writerow(
                [
                    entry.id,
                    entry.timestamp.isoformat(sep=" ", timespec="seconds"),
                    mood_key,
                    MOOD_NAMES.get(mood_key, mood_key),
                    get_mood_emoji(mood_key),
                    REASON_NAMES.get(entry.reason or "none", "Без причины"),
                    entry.comment or "",
                ]
            )
    path.chmod(0o600)
    return path


def create_json_export_file(entries: list, filename_prefix: str) -> Path:
    payload = []
    for entry in entries:
        mood_key = get_entry_mood_key(entry)
        payload.append(
            {
                "id": entry.id,
                "timestamp": entry.timestamp.isoformat(sep=" ", timespec="seconds"),
                "state_key": mood_key,
                "state_label": MOOD_NAMES.get(mood_key, mood_key),
                "emoji": get_mood_emoji(mood_key),
                "reason": REASON_NAMES.get(entry.reason or "none", "Без причины"),
                "comment": entry.comment or "",
            }
        )

    fd, path_str = tempfile.mkstemp(prefix=filename_prefix, suffix=".json")
    os.close(fd)
    path = Path(path_str)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    path.chmod(0o600)
    return path

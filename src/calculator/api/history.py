"""История вычислений в памяти процесса.

Хранилище однопроцессное: при запуске uvicorn с несколькими воркерами
(``--workers`` больше 1) история не будет общей между воркерами.
"""

import threading
from collections import deque
from datetime import datetime, timezone
from typing import TypedDict

MAX_HISTORY = 50


class HistoryEntry(TypedDict):
    """Запись истории вычисления."""

    expression: str
    result: float
    created_at: str


_lock = threading.Lock()
_history: deque[HistoryEntry] = deque(maxlen=MAX_HISTORY)


def add(expression: str, result: float) -> HistoryEntry:
    """Добавить запись в историю и вернуть её."""
    item: HistoryEntry = {
        "expression": expression,
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        _history.append(item)
    return item


def list_items(limit: int | None = None) -> list[HistoryEntry]:
    """Вернуть записи истории (сначала новые)."""
    with _lock:
        items = list(_history)
    items.reverse()
    if limit is not None:
        items = items[:limit]
    return items


def clear() -> None:
    """Очистить историю."""
    with _lock:
        _history.clear()

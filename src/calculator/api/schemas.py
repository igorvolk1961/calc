"""Pydantic-схемы API."""

from pydantic import BaseModel, Field


class CalculateRequest(BaseModel):
    """Запрос на вычисление выражения."""

    expression: str = Field(..., min_length=1, max_length=1000)


class CalculateResponse(BaseModel):
    """Результат вычисления."""

    expression: str
    result: float
    result_text: str


class HistoryItem(BaseModel):
    """Одна запись истории."""

    expression: str
    result: float
    created_at: str


class HistoryResponse(BaseModel):
    """Список записей истории."""

    items: list[HistoryItem]

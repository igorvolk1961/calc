"""HTTP-маршруты API калькулятора."""

from fastapi import APIRouter, HTTPException, Query, Response, status

from calculator.api import history
from calculator.api.schemas import (
    CalculateRequest,
    CalculateResponse,
    HistoryItem,
    HistoryResponse,
)
from calculator.errors import CalculationError
from calculator.evaluator import evaluate, format_number

router = APIRouter(prefix="/api")


@router.post("/calculate", response_model=CalculateResponse)
def calculate(payload: CalculateRequest) -> CalculateResponse:
    """Вычислить выражение и сохранить результат в истории."""
    try:
        result = evaluate(payload.expression)
    except CalculationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    history.add(payload.expression, result)
    return CalculateResponse(
        expression=payload.expression,
        result=result,
        result_text=format_number(result),
    )


@router.get("/history", response_model=HistoryResponse)
def get_history(limit: int = Query(20, ge=1, le=history.MAX_HISTORY)) -> HistoryResponse:
    """Вернуть последние вычисления (сначала новые)."""
    items = [HistoryItem(**item) for item in history.list_items(limit)]
    return HistoryResponse(items=items)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def delete_history() -> Response:
    """Очистить историю вычислений."""
    history.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

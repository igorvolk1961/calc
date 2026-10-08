# Calculator

Веб-калькулятор на Python: бэкенд на FastAPI вычисляет математические выражения,
фронтенд — статическая HTML/JS-страница с клавиатурой, результатом и историей.

## Возможности

- Операции: `+ - * /`, `^` (степень), унарный минус, круглые скобки.
- Функции: `sqrt, abs, sin, cos, tan, log` (натуральный), `log10, exp`.
- Константы: `pi`, `e`. Углы в радианах.
- Собственный безопасный парсер (shunting-yard → RPN), без `eval`.
- История последних 50 вычислений в памяти процесса.

## Структура проекта

```
test_kilo_code/
├── src/calculator/
│   ├── __init__.py          # публичный API
│   ├── core.py              # базовые арифметические операции
│   ├── errors.py            # CalculationError
│   ├── evaluator.py         # токенайзер, парсер, вычисление выражений
│   ├── __main__.py          # CLI-интерфейс
│   ├── api/
│   │   ├── main.py          # FastAPI-приложение
│   │   ├── routes.py        # /api/calculate, /api/history
│   │   ├── schemas.py       # pydantic-схемы
│   │   └── history.py       # история в памяти
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── tests/
│   ├── test_core.py
│   ├── test_evaluator.py
│   └── test_api.py
├── pyproject.toml
├── .gitignore
└── README.md
```

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Запуск веб-приложения

```bash
uvicorn calculator.api.main:app --reload
```

Откройте http://127.0.0.1:8000 — доступны клавиатура, результат и история.
Документация API: http://127.0.0.1:8000/docs.

## Запуск CLI

```bash
python -m calculator
```

## API

```bash
# Вычислить выражение
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "2 + 3 * (4 - 1)"}'

# История
curl "http://127.0.0.1:8000/api/history?limit=20"

# Очистить историю
curl -X DELETE http://127.0.0.1:8000/api/history
```

## Тесты и линтер

```bash
pytest
./scripts/lint.sh   # ruff format + ruff check --fix + mypy
```

Отдельные проверки:

```bash
ruff format .          # автоформатирование
ruff check --fix .     # линт с автоисправлениями
mypy                   # проверка типов
```

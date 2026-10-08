#!/usr/bin/env bash
# Запуск всех линтеров проекта: форматирование, проверка стиля и типов.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
fi

echo "==> ruff format"
"$PYTHON" -m ruff format .

echo "==> ruff check --fix"
"$PYTHON" -m ruff check --fix .

echo "==> mypy"
"$PYTHON" -m mypy

echo "Все проверки пройдены."

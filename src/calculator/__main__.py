"""Точка входа CLI: python -m calculator."""

from calculator.errors import CalculationError
from calculator.evaluator import evaluate, format_number


def main() -> None:
    print("Калькулятор. Введите выражение (например '2 + 3 * (4 - 1)') или 'q' для выхода.")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if raw.lower() in {"q", "quit", "exit"}:
            break
        if not raw:
            continue
        try:
            result = evaluate(raw)
        except CalculationError as exc:
            print(f"Ошибка: {exc}")
        else:
            print(f"= {format_number(result)}")


if __name__ == "__main__":
    main()

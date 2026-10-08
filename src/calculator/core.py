"""Арифметические операции калькулятора."""


def add(a: float, b: float) -> float:
    """Вернуть сумму a и b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Вернуть разность a и b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Вернуть произведение a и b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Вернуть частное a и b.

    Raises:
        ZeroDivisionError: если b равно нулю.
    """
    if b == 0:
        raise ZeroDivisionError("деление на ноль невозможно")
    return a / b

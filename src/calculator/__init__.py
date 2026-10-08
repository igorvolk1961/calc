"""Пакет калькулятора."""

from calculator.core import add, divide, multiply, subtract
from calculator.errors import CalculationError
from calculator.evaluator import evaluate, format_number

__all__ = [
    "CalculationError",
    "__version__",
    "add",
    "divide",
    "evaluate",
    "format_number",
    "multiply",
    "subtract",
]
__version__ = "0.2.0"

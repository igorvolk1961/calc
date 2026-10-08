import math

import pytest

from calculator.errors import CalculationError
from calculator.evaluator import evaluate, format_number


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2 + 3", 5.0),
        ("2 + 3 * (4 - 1)", 11.0),
        ("(2 + 3) * 4", 20.0),
        ("10 / 4", 2.5),
        ("1 - 2 - 3", -4.0),
        ("2 ^ 3", 8.0),
        ("2 ^ 3 ^ 2", 512.0),
        ("-2 ^ 2", -4.0),
        ("2 ^ -2", 0.25),
        ("-2 * 3", -6.0),
        ("3 * -2", -6.0),
        ("--2", 2.0),
        ("1e-3", 0.001),
        (".5 + .5", 1.0),
        ("sqrt(9)", 3.0),
        ("sqrt(9) + pi", math.sqrt(9) + math.pi),
        ("abs(-4)", 4.0),
        ("log(e)", 1.0),
        ("log10(100)", 2.0),
        ("sqrt(abs(-16))", 4.0),
        ("  7   ", 7.0),
    ],
)
def test_evaluate_valid(expression: str, expected: float) -> None:
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "1/0",
        "2(3)",
        "sqrt(9",
        "2 +",
        "+",
        "unknown(2)",
        "foo",
        "1 $ 2",
        "()",
        ")(",
        "sqrt 9",
        "sqrt 9 + 4",
        "abs -4",
        "π",
    ],
)
def test_evaluate_invalid(expression: str) -> None:
    with pytest.raises(CalculationError):
        evaluate(expression)


def test_evaluate_log_domain_error() -> None:
    with pytest.raises(CalculationError):
        evaluate("log(-1)")


def test_evaluate_sqrt_domain_error() -> None:
    with pytest.raises(CalculationError):
        evaluate("sqrt(-1)")


def test_evaluate_too_long() -> None:
    with pytest.raises(CalculationError):
        evaluate("1+" * 600 + "1")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (5.0, "5"),
        (-3.0, "-3"),
        (2.5, "2.5"),
        (0.1 + 0.2, "0.30000000000000004"),
        (1e300, "1e+300"),
    ],
)
def test_format_number(value: float, expected: str) -> None:
    assert format_number(value) == expected

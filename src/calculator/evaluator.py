"""Разбор и вычисление арифметических выражений.

Грамматика поддерживает операции ``+ - * / ^``, унарный минус, круглые скобки,
функции (``sqrt, abs, sin, cos, tan, log, log10, exp``) и константы (``pi, e``).
Собственный парсер (shunting-yard → RPN), без использования ``eval``.
"""

import math
import re
from collections.abc import Callable
from typing import cast

from calculator.core import add, divide, multiply, subtract
from calculator.errors import CalculationError

NUMBER_RE = re.compile(r"(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?")
IDENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")

FUNCTIONS: dict[str, Callable[[float], float]] = {
    "sqrt": math.sqrt,
    "abs": abs,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
}

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "unary-": 3, "^": 4}
LEFT_ASSOC = {"+", "-", "*", "/"}
MAX_EXPRESSION_LENGTH = 1000


def evaluate(expression: str) -> float:
    """Вычислить выражение и вернуть результат.

    Raises:
        CalculationError: при синтаксической ошибке, неизвестной функции или
            константе, делении на ноль и других некорректных операциях.
    """
    if expression is None:
        raise CalculationError("выражение не задано")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise CalculationError("выражение слишком длинное")
    tokens = tokenize(expression)
    if not tokens:
        raise CalculationError("пустое выражение")
    rpn = to_rpn(tokens)
    return eval_rpn(rpn)


def tokenize(expression: str) -> list[tuple[str, object]]:
    """Разбить выражение на токены."""
    tokens: list[tuple[str, object]] = []
    i = 0
    length = len(expression)
    while i < length:
        ch = expression[i]
        if ch.isspace():
            i += 1
            continue
        number = NUMBER_RE.match(expression, i)
        if number:
            tokens.append(("num", float(number.group())))
            i = number.end()
            continue
        if ch.isalpha():
            ident = IDENT_RE.match(expression, i)
            if ident is None:
                raise CalculationError(f"недопустимый символ: {ch!r}")
            name = ident.group()
            i = ident.end()
            if name in CONSTANTS:
                tokens.append(("num", CONSTANTS[name]))
            elif name in FUNCTIONS:
                tokens.append(("func", name))
            else:
                raise CalculationError(f"неизвестная функция или константа: {name}")
            continue
        if ch in "+-*/^":
            tokens.append(("op", ch))
            i += 1
            continue
        if ch == "(":
            tokens.append(("lparen", ch))
            i += 1
            continue
        if ch == ")":
            tokens.append(("rparen", ch))
            i += 1
            continue
        raise CalculationError(f"недопустимый символ: {ch!r}")
    return tokens


def to_rpn(tokens: list[tuple[str, object]]) -> list[tuple[str, object]]:
    """Преобразовать токены в обратную польскую запись (shunting-yard)."""
    output: list[tuple[str, object]] = []
    stack: list[tuple[str, object]] = []
    prev_kind: str | None = None
    for index, token in enumerate(tokens):
        kind = token[0]
        if kind == "num":
            output.append(token)
        elif kind == "func":
            next_kind = tokens[index + 1][0] if index + 1 < len(tokens) else None
            if next_kind != "lparen":
                raise CalculationError(f"после функции {token[1]} ожидается '('")
            stack.append(token)
        elif kind == "lparen":
            stack.append(token)
        elif kind == "rparen":
            while stack and stack[-1][0] != "lparen":
                output.append(stack.pop())
            if not stack:
                raise CalculationError("несбалансированные скобки")
            stack.pop()
            if stack and stack[-1][0] == "func":
                output.append(stack.pop())
        elif kind == "op":
            op = str(token[1])
            if op == "-" and prev_kind in (None, "op", "lparen"):
                op = "unary-"
            if op == "unary-":
                stack.append(("op", op))
            else:
                while (
                    stack
                    and stack[-1][0] == "op"
                    and (
                        PRECEDENCE[str(stack[-1][1])] > PRECEDENCE[op]
                        or (PRECEDENCE[str(stack[-1][1])] == PRECEDENCE[op] and op in LEFT_ASSOC)
                    )
                ):
                    output.append(stack.pop())
                stack.append(("op", op))
        prev_kind = kind
    while stack:
        top = stack.pop()
        if top[0] == "lparen":
            raise CalculationError("несбалансированные скобки")
        output.append(top)
    return output


def eval_rpn(rpn: list[tuple[str, object]]) -> float:
    """Вычислить выражение в обратной польской записи."""
    stack: list[float] = []
    for kind, value in rpn:
        if kind == "num":
            stack.append(cast(float, value))
        elif kind == "op":
            _apply_operator(str(value), stack)
        elif kind == "func":
            _apply_function(str(value), stack)
    if len(stack) != 1:
        raise CalculationError("некорректное выражение")
    result = stack[0]
    if not math.isfinite(result):
        raise CalculationError("результат не является конечным числом")
    return result


def _apply_operator(op: str, stack: list[float]) -> None:
    if op == "unary-":
        if not stack:
            raise CalculationError("недостаточно операндов")
        stack.append(-stack.pop())
        return
    if len(stack) < 2:
        raise CalculationError("недостаточно операндов")
    right = stack.pop()
    left = stack.pop()
    if op == "+":
        stack.append(add(left, right))
    elif op == "-":
        stack.append(subtract(left, right))
    elif op == "*":
        stack.append(multiply(left, right))
    elif op == "/":
        try:
            stack.append(divide(left, right))
        except ZeroDivisionError as exc:
            raise CalculationError(str(exc)) from exc
    elif op == "^":
        try:
            result = left**right
        except (OverflowError, ZeroDivisionError, ValueError) as exc:
            raise CalculationError(f"ошибка возведения в степень: {exc}") from exc
        if isinstance(result, complex):
            raise CalculationError("результат возведения в степень не является действительным")
        stack.append(result)
    else:
        raise CalculationError(f"неизвестная операция: {op}")


def _apply_function(name: str, stack: list[float]) -> None:
    if not stack:
        raise CalculationError("недостаточно операндов")
    argument = stack.pop()
    function = FUNCTIONS[name]
    try:
        result = function(argument)
    except (ValueError, OverflowError) as exc:
        raise CalculationError(f"ошибка вычисления {name}: {exc}") from exc
    stack.append(float(result))


def format_number(value: float) -> str:
    """Отформатировать число: целые без хвостового ``.0``."""
    if math.isfinite(value) and value == int(value) and abs(value) < 1e16:
        return str(int(value))
    return repr(value)

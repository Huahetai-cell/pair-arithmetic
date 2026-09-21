from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Protocol


def format_fraction(value: Fraction) -> str:
    """Format a non-negative fraction using integer, a/b, or w’a/b."""
    if value < 0:
        return "−" + format_fraction(-value)
    whole, remainder = divmod(value.numerator, value.denominator)
    if remainder == 0:
        return str(whole)
    if whole == 0:
        return f"{remainder}/{value.denominator}"
    return f"{whole}’{remainder}/{value.denominator}"


def parse_fraction(text: str) -> Fraction:
    token = text.strip().replace("'", "’")
    if "’" in token:
        whole_text, part = token.split("’", 1)
        numerator_text, denominator_text = part.split("/", 1)
        whole = int(whole_text)
        numerator = int(numerator_text)
        denominator = int(denominator_text)
        if whole < 0 or denominator <= 0 or numerator <= 0 or numerator >= denominator:
            raise ValueError(f"invalid mixed fraction: {text}")
        return Fraction(whole * denominator + numerator, denominator)
    if "/" in token:
        numerator_text, denominator_text = token.split("/", 1)
        return Fraction(int(numerator_text), int(denominator_text))
    value = int(token)
    if value < 0:
        raise ValueError(f"negative input is not allowed: {text}")
    return Fraction(value)


class Operator(Enum):
    ADD = ("+", 1)
    SUBTRACT = ("−", 1)
    MULTIPLY = ("×", 2)
    DIVIDE = ("÷", 2)

    def __init__(self, symbol: str, precedence: int) -> None:
        self.symbol = symbol
        self.precedence = precedence

    @property
    def commutative(self) -> bool:
        return self in (Operator.ADD, Operator.MULTIPLY)


class Expression(Protocol):
    value: Fraction
    operator_count: int
    precedence: int
    canonical_key: str

    def render(self) -> str: ...


@dataclass(frozen=True, slots=True)
class Number:
    value: Fraction
    operator_count: int = field(default=0, init=False)
    precedence: int = field(default=3, init=False)
    canonical_key: str = field(init=False)

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("exercise numbers must not be negative")
        object.__setattr__(self, "canonical_key", f"N[{self.value.numerator}/{self.value.denominator}]")

    def render(self) -> str:
        return format_fraction(self.value)


@dataclass(frozen=True, slots=True)
class Binary:
    left: Expression
    operator: Operator
    right: Expression
    value: Fraction = field(init=False)
    operator_count: int = field(init=False)
    precedence: int = field(init=False)
    canonical_key: str = field(init=False)

    def __post_init__(self) -> None:
        if self.operator is Operator.ADD:
            value = self.left.value + self.right.value
        elif self.operator is Operator.SUBTRACT:
            value = self.left.value - self.right.value
        elif self.operator is Operator.MULTIPLY:
            value = self.left.value * self.right.value
        else:
            value = self.left.value / self.right.value
        left_key, right_key = self.left.canonical_key, self.right.canonical_key
        if self.operator.commutative and left_key > right_key:
            left_key, right_key = right_key, left_key
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "operator_count", self.left.operator_count + self.right.operator_count + 1)
        object.__setattr__(self, "precedence", self.operator.precedence)
        object.__setattr__(self, "canonical_key", f"{self.operator.name}({left_key},{right_key})")

    def render(self) -> str:
        return f"{self._render_child(self.left, False)} {self.operator.symbol} {self._render_child(self.right, True)}"

    def _render_child(self, child: Expression, right_child: bool) -> str:
        needs_parentheses = child.precedence < self.precedence or (
            right_child and child.precedence == self.precedence
        )
        rendered = child.render()
        return f"({rendered})" if needs_parentheses else rendered


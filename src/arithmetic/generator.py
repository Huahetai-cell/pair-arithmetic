from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from .expression import Binary, Expression, Number, Operator


@dataclass(slots=True)
class GenerationStats:
    candidates: int = 0
    constraint_rejects: int = 0
    duplicates: int = 0


@dataclass(frozen=True, slots=True)
class GenerationResult:
    exercises: tuple[Expression, ...]
    stats: GenerationStats


class ExerciseGenerator:
    def generate(
        self,
        count: int,
        value_range: int,
        seed: int | None = None,
        key_strategy: Callable[[Expression], str] | None = None,
    ) -> GenerationResult:
        if count <= 0:
            raise ValueError("exercise count must be positive")
        if value_range <= 0:
            raise ValueError("range must be positive")
        random_source = random.Random(seed)
        key_strategy = key_strategy or (lambda expression: expression.canonical_key)
        maximum_attempts = max(20_000, count * 2_000)
        stats = GenerationStats()
        exercises: list[Expression] = []
        seen: set[str] = set()
        while len(exercises) < count and stats.candidates < maximum_attempts:
            stats.candidates += 1
            candidate = self._build(random_source, value_range, random_source.randint(1, 3), stats)
            if candidate is None:
                continue
            key = key_strategy(candidate)
            if key in seen:
                stats.duplicates += 1
                continue
            seen.add(key)
            exercises.append(candidate)
        if len(exercises) != count:
            raise RuntimeError(
                f"could generate only {len(exercises)} unique exercises after {maximum_attempts} "
                "attempts; increase -r or reduce -n"
            )
        return GenerationResult(tuple(exercises), stats)

    def _build(
        self, random_source: random.Random, value_range: int, operators: int, stats: GenerationStats
    ) -> Expression | None:
        if operators == 0:
            return self._atom(random_source, value_range)
        left_operators = random_source.randrange(operators)
        left = self._build(random_source, value_range, left_operators, stats)
        right = self._build(random_source, value_range, operators - 1 - left_operators, stats)
        if left is None or right is None:
            return None
        operator = random_source.choice(tuple(Operator))
        if operator is Operator.SUBTRACT and left.value < right.value:
            stats.constraint_rejects += 1
            return None
        if operator is Operator.DIVIDE and (left.value <= 0 or left.value >= right.value):
            stats.constraint_rejects += 1
            return None
        try:
            expression = Binary(left, operator, right)
        except ZeroDivisionError:
            stats.constraint_rejects += 1
            return None
        if operator is Operator.DIVIDE and not (0 < expression.value < 1):
            stats.constraint_rejects += 1
            return None
        return expression

    @staticmethod
    def _atom(random_source: random.Random, value_range: int) -> Number:
        if value_range < 3 or random_source.choice((True, False)):
            return Number(Fraction(random_source.randrange(value_range)))
        denominator = random_source.randrange(2, value_range)
        numerator = random_source.randrange(1, value_range * denominator)
        return Number(Fraction(numerator, denominator))


from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .expression import parse_fraction
from .parser import ExpressionParser

EXERCISE_LINE = re.compile(r"^\s*(\d+)\.\s*(.*?)\s*=\s*$")
ANSWER_LINE = re.compile(r"^\s*(\d+)\)\s*(.*?)\s*$")


@dataclass(frozen=True, slots=True)
class GradeResult:
    correct: tuple[int, ...]
    wrong: tuple[int, ...]

    def format(self) -> str:
        return self._line("Correct", self.correct) + "\n" + self._line("Wrong", self.wrong) + "\n"

    @staticmethod
    def _line(label: str, numbers: tuple[int, ...]) -> str:
        return f"{label}: {len(numbers)} ({', '.join(map(str, numbers))})"


class Grader:
    def __init__(self) -> None:
        self._parser = ExpressionParser()

    def grade(self, exercise_file: Path, answer_file: Path) -> GradeResult:
        answers: dict[int, str] = {}
        for line in answer_file.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            match = ANSWER_LINE.fullmatch(line)
            if match:
                answers[int(match.group(1))] = match.group(2).strip()

        correct: list[int] = []
        wrong: list[int] = []
        for line in exercise_file.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            match = EXERCISE_LINE.fullmatch(line)
            if not match:
                raise ValueError(f"invalid exercise line: {line}")
            number = int(match.group(1))
            try:
                expected = self._parser.parse(match.group(2)).value
                supplied = answers.get(number)
                if supplied is not None and parse_fraction(supplied) == expected:
                    correct.append(number)
                else:
                    wrong.append(number)
            except (ArithmeticError, ValueError):
                wrong.append(number)
        return GradeResult(tuple(correct), tuple(wrong))


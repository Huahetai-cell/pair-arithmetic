from __future__ import annotations

import io
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from arithmetic.cli import main
from arithmetic.expression import Binary, Number, Operator, format_fraction, parse_fraction
from arithmetic.generator import ExerciseGenerator
from arithmetic.grader import Grader
from arithmetic.parser import ExpressionParser


class FractionTests(unittest.TestCase):
    def test_parse_reduce_and_format(self) -> None:
        self.assertEqual(Fraction(1, 2), parse_fraction("2/4"))
        self.assertEqual(Fraction(19, 8), parse_fraction("2'3/8"))
        self.assertEqual("2’3/8", format_fraction(Fraction(19, 8)))

    def test_exact_example(self) -> None:
        self.assertEqual("7/24", format_fraction(Fraction(1, 6) + Fraction(1, 8)))

    def test_invalid_fraction(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            parse_fraction("1/0")
        with self.assertRaises(ValueError):
            parse_fraction("1’4/4")


class ExpressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ExpressionParser()

    def test_precedence_and_ascii_aliases(self) -> None:
        self.assertEqual(Fraction(7), self.parser.parse("1 + 2 * 3 =").value)
        self.assertEqual(Fraction(3, 4), self.parser.parse("1 - 1 / 4").value)

    def test_render_round_trip_preserves_tree(self) -> None:
        expression = Binary(Number(Fraction(3)), Operator.ADD,
                            Binary(Number(Fraction(2)), Operator.ADD, Number(Fraction(1))))
        self.assertEqual("3 + (2 + 1)", expression.render())
        self.assertEqual(expression.canonical_key, self.parser.parse(expression.render()).canonical_key)

    def test_required_duplicate_examples(self) -> None:
        self.assertEqual(self.parser.parse("23 + 45").canonical_key,
                         self.parser.parse("45 + 23").canonical_key)
        self.assertEqual(self.parser.parse("3 + (2 + 1)").canonical_key,
                         self.parser.parse("1 + 2 + 3").canonical_key)
        self.assertNotEqual(self.parser.parse("1 + 2 + 3").canonical_key,
                            self.parser.parse("3 + 2 + 1").canonical_key)


class GeneratorTests(unittest.TestCase):
    def test_generated_exercises_meet_all_constraints(self) -> None:
        for seed in (1, 2, 3, 99, 2026):
            result = ExerciseGenerator().generate(500, 10, seed)
            keys: set[str] = set()
            for expression in result.exercises:
                self.assertIn(expression.operator_count, (1, 2, 3))
                self.assertNotIn(expression.canonical_key, keys)
                keys.add(expression.canonical_key)
                self._verify_tree(expression)

    def test_ten_thousand_unique_exercises(self) -> None:
        result = ExerciseGenerator().generate(10_000, 10, 42)
        self.assertEqual(10_000, len(result.exercises))
        self.assertEqual(10_000, len({item.canonical_key for item in result.exercises}))

    def test_impossible_request_stops(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "increase -r"):
            ExerciseGenerator().generate(100, 1, 1)

    def _verify_tree(self, expression) -> None:
        if not isinstance(expression, Binary):
            self.assertGreaterEqual(expression.value, 0)
            return
        self._verify_tree(expression.left)
        self._verify_tree(expression.right)
        if expression.operator is Operator.SUBTRACT:
            self.assertGreaterEqual(expression.left.value, expression.right.value)
        if expression.operator is Operator.DIVIDE:
            self.assertLess(Fraction(0), expression.value)
            self.assertLess(expression.value, Fraction(1))


class GraderAndCliTests(unittest.TestCase):
    def test_grader_handles_correct_wrong_missing_and_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "e.txt").write_text(
                "1. 1/6 + 1/8 =\n2. 3 × 4 =\n3. 8 − 3 =\n4. 1 ÷ 2 =\n", encoding="utf-8"
            )
            (root / "a.txt").write_text("1) 7/24\n2) 11\n4) nonsense\n", encoding="utf-8")
            result = Grader().grade(root / "e.txt", root / "a.txt")
            self.assertEqual((1,), result.correct)
            self.assertEqual((2, 3, 4), result.wrong)
            self.assertEqual("Correct: 1 (1)\nWrong: 3 (2, 3, 4)\n", result.format())

    def test_generation_writes_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(0, main(["-n", "20", "-r", "10"], root))
            self.assertEqual(20, len((root / "Exercises.txt").read_text(encoding="utf-8").splitlines()))
            self.assertEqual(20, len((root / "Answers.txt").read_text(encoding="utf-8").splitlines()))

    def test_missing_range_prints_help_and_fails(self) -> None:
        with self.assertRaises(SystemExit) as raised, patch("sys.stderr", new_callable=io.StringIO) as error:
            main(["-n", "10"])
        self.assertEqual(2, raised.exception.code)
        self.assertIn("-n 和 -r", error.getvalue())

    def test_grading_mode_writes_grade_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "e.txt").write_text("1. 1 + 2 =\n", encoding="utf-8")
            (root / "a.txt").write_text("1) 3\n", encoding="utf-8")
            self.assertEqual(0, main(["-e", str(root / "e.txt"), "-a", str(root / "a.txt")], root))
            self.assertIn("Correct: 1 (1)", (root / "Grade.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

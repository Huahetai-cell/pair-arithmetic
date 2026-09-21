from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .expression import format_fraction
from .generator import ExerciseGenerator
from .grader import Grader


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"错误: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = ArgumentParser(
        prog="Myapp",
        description="自动生成小学四则运算题目，或根据题目文件批改答案。",
    )
    parser.add_argument("-n", type=positive_integer, help="生成题目的数量（生成模式必填）")
    parser.add_argument("-r", type=positive_integer, dest="value_range", help="数值范围（生成模式必填）")
    parser.add_argument("-e", type=Path, metavar="EXERCISES", help="待批改的题目文件")
    parser.add_argument("-a", type=Path, metavar="ANSWERS", help="待批改的答案文件")
    return parser


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("必须是正整数")
    return parsed


def main(argv: list[str] | None = None, working_directory: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    generation_selected = args.n is not None or args.value_range is not None
    grading_selected = args.e is not None or args.a is not None
    if generation_selected == grading_selected:
        parser.error("必须且只能选择生成模式 (-n/-r) 或判题模式 (-e/-a)")
    directory = working_directory or Path.cwd()
    try:
        if generation_selected:
            if args.n is None or args.value_range is None:
                parser.error("生成模式必须同时提供 -n 和 -r")
            result = ExerciseGenerator().generate(args.n, args.value_range)
            exercise_lines = [f"{index}. {expression.render()} =" for index, expression in enumerate(result.exercises, 1)]
            answer_lines = [f"{index}) {format_fraction(expression.value)}" for index, expression in enumerate(result.exercises, 1)]
            (directory / "Exercises.txt").write_text("\n".join(exercise_lines) + "\n", encoding="utf-8")
            (directory / "Answers.txt").write_text("\n".join(answer_lines) + "\n", encoding="utf-8")
            print(f"已生成 {args.n} 道题目：{(directory / 'Exercises.txt').resolve()}")
        else:
            if args.e is None or args.a is None:
                parser.error("判题模式必须同时提供 -e 和 -a")
            result = Grader().grade(args.e, args.a)
            (directory / "Grade.txt").write_text(result.format(), encoding="utf-8")
            print(result.format(), end="")
            print(f"统计结果：{(directory / 'Grade.txt').resolve()}")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"错误: {error}", file=sys.stderr)
        return 2

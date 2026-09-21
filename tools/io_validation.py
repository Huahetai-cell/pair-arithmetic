from __future__ import annotations

import re
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from arithmetic.expression import parse_fraction  # noqa: E402
from arithmetic.parser import ExpressionParser  # noqa: E402


@dataclass(slots=True)
class Case:
    name: str
    input_text: str
    expected: str
    passed: bool
    observation: str


def invoke(command: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=90, check=False, env=environment,
    )


def text_preview(data: bytes) -> str:
    for encoding in ("utf-8", "gb18030"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    text = text.strip().replace("\r", "").replace("\n", " / ")
    return text[:180] or "(no console output)"


def validate_generated(root: Path, count: int) -> tuple[bool, str]:
    exercise_file, answer_file = root / "Exercises.txt", root / "Answers.txt"
    if not exercise_file.exists() or not answer_file.exists():
        return False, "required output file is missing"
    exercises = exercise_file.read_text(encoding="utf-8").splitlines()
    answers = answer_file.read_text(encoding="utf-8").splitlines()
    if len(exercises) != count or len(answers) != count:
        return False, f"line counts are {len(exercises)}/{len(answers)}"
    parser, keys = ExpressionParser(), set()
    for index, (exercise, answer) in enumerate(zip(exercises, answers, strict=True), 1):
        exercise_match = re.fullmatch(r"(\d+)\. (.+) =", exercise)
        answer_match = re.fullmatch(r"(\d+)\) (\d+(?:’\d+/\d+|/\d+)?)", answer)
        if not exercise_match or not answer_match:
            return False, f"format mismatch at line {index}"
        expression = parser.parse(exercise_match.group(2))
        if int(exercise_match.group(1)) != index or int(answer_match.group(1)) != index:
            return False, f"number mismatch at line {index}"
        if expression.value != parse_fraction(answer_match.group(2)):
            return False, f"answer mismatch at line {index}"
        if expression.canonical_key in keys:
            return False, f"duplicate at line {index}"
        keys.add(expression.canonical_key)
    return True, f"{count} lines, exact answers, valid numbering, no duplicates"


def main() -> int:
    executable = ROOT / "dist" / "Myapp.exe"
    runner = [str(executable)] if executable.exists() else [sys.executable, str(ROOT / "Myapp.py")]
    runner_label = "dist/Myapp.exe" if executable.exists() else "python Myapp.py"
    cases: list[Case] = []
    started_all = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="pair-arithmetic-io-") as temporary:
        root = Path(temporary)

        def command(name: str, arguments: list[str], expected_code: int, expected: str) -> subprocess.CompletedProcess[bytes]:
            result = invoke(runner + arguments, root)
            passed = result.returncode == expected_code
            stream = result.stdout if expected_code == 0 else result.stderr
            cases.append(Case(name, " ".join(arguments) or "(no arguments)", expected, passed,
                              f"exit={result.returncode}; {text_preview(stream)}"))
            return result

        command("Help", ["--help"], 0, "exit 0 and usage text")
        command("Missing -r", ["-n", "10"], 2, "exit 2 and help")
        command("Zero count", ["-n", "0", "-r", "10"], 2, "exit 2")
        command("Non-integer count", ["-n", "abc", "-r", "10"], 2, "exit 2")
        command("Negative range", ["-n", "10", "-r", "-1"], 2, "exit 2")
        command("Unknown option", ["--unknown", "1"], 2, "exit 2")
        command("Mixed modes", ["-n", "1", "-r", "10", "-e", "e.txt", "-a", "a.txt"], 2, "exit 2")
        command("Missing grading files", ["-e", "missing-e.txt", "-a", "missing-a.txt"], 2, "exit 2")

        result = command("Minimum range", ["-n", "1", "-r", "1"], 0, "one valid exercise")
        ok, detail = validate_generated(root, 1) if result.returncode == 0 else (False, "generation failed")
        cases[-1].passed &= ok
        cases[-1].observation += f"; {detail}"

        result = command("Normal generation", ["-n", "100", "-r", "10"], 0, "100 valid exercises and answers")
        ok, detail = validate_generated(root, 100) if result.returncode == 0 else (False, "generation failed")
        cases[-1].passed &= ok
        cases[-1].observation += f"; {detail}"

        result = command("10,000 generation", ["-n", "10000", "-r", "10"], 0, "10,000 valid unique exercises")
        ok, detail = validate_generated(root, 10_000) if result.returncode == 0 else (False, "generation failed")
        cases[-1].passed &= ok
        cases[-1].observation += f"; {detail}"

        (root / "grade-e.txt").write_text(
            "1. 1/6 + 1/8 =\n2. 3 × 4 =\n3. 8 − 3 =\n4. 1 ÷ 2 =\n5. 2’3/8 + 5/8 =\n",
            encoding="utf-8-sig",
        )
        (root / "grade-a.txt").write_text("1) 7/24\n2) 11\n4) bad\n5) 3\n", encoding="utf-8-sig")
        result = command("Grading matrix", ["-e", "grade-e.txt", "-a", "grade-a.txt"], 0,
                         "Correct 1,5; Wrong 2,3,4")
        grade = (root / "Grade.txt").read_text(encoding="utf-8") if (root / "Grade.txt").exists() else ""
        expected_grade = "Correct: 2 (1, 5)\nWrong: 3 (2, 3, 4)\n"
        cases[-1].passed &= grade == expected_grade
        cases[-1].observation += "; Grade.txt=" + grade.strip().replace("\n", " / ")

        command("Overwrite outputs", ["-n", "3", "-r", "10"], 0, "old 10,000-line files replaced by 3 lines")
        ok, detail = validate_generated(root, 3)
        cases[-1].passed &= ok
        cases[-1].observation += f"; {detail}"

    elapsed = time.perf_counter() - started_all
    passed_count = sum(item.passed for item in cases)
    rows = "\n".join(
        f"| {index} | {item.name} | `{item.input_text}` | {item.expected} | {'PASS' if item.passed else 'FAIL'} | {item.observation.replace('|', '/')} |"
        for index, item in enumerate(cases, 1)
    )
    report = f"""# 输入输出验收报告

- 执行入口：`{runner_label}`
- 用例数量：{len(cases)}
- 通过：{passed_count}
- 失败：{len(cases) - passed_count}
- 总耗时：{elapsed:.2f}s

| # | 场景 | 输入参数 | 预期 | 结果 | 实际观察 |
|---:|---|---|---|---|---|
{rows}

## 完备性结论

检查覆盖正常输入、最小范围、万人题、缺失参数、非法整数、未知参数、模式冲突、文件缺失、UTF-8 BOM、带分数、正确/错误/缺失/非法答案、重复检测、答案精确性及覆盖写行为。所有生成题均通过重新解析和精确分数求值验证。
"""
    destination = ROOT / "docs" / "io-validation.md"
    destination.write_text(report, encoding="utf-8")
    print(f"{passed_count}/{len(cases)} I/O cases passed; report: {destination}")
    return 0 if passed_count == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())

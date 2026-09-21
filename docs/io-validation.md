# 输入输出验收报告

- 执行入口：`dist/Myapp.exe`
- 用例数量：13
- 通过：13
- 失败：0
- 总耗时：10.11s

| # | 场景 | 输入参数 | 预期 | 结果 | 实际观察 |
|---:|---|---|---|---|---|
| 1 | Help | `--help` | exit 0 and usage text | PASS | exit=0; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] /  / 自动生成小学四则运算题目，或根据题目文件批改答案。 /  / options: /   -h, --help      show this help message and exit /   -n N      |
| 2 | Missing -r | `-n 10` | exit 2 and help | PASS | exit=2; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] / 错误: 生成模式必须同时提供 -n 和 -r |
| 3 | Zero count | `-n 0 -r 10` | exit 2 | PASS | exit=2; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] / 错误: argument -n: 必须是正整数 |
| 4 | Non-integer count | `-n abc -r 10` | exit 2 | PASS | exit=2; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] / 错误: argument -n: invalid positive_integer value: 'abc' |
| 5 | Negative range | `-n 10 -r -1` | exit 2 | PASS | exit=2; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] / 错误: argument -r: 必须是正整数 |
| 6 | Unknown option | `--unknown 1` | exit 2 | PASS | exit=2; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] / 错误: unrecognized arguments: --unknown 1 |
| 7 | Mixed modes | `-n 1 -r 10 -e e.txt -a a.txt` | exit 2 | PASS | exit=2; usage: Myapp [-h] [-n N] [-r VALUE_RANGE] [-e EXERCISES] [-a ANSWERS] / 错误: 必须且只能选择生成模式 (-n/-r) 或判题模式 (-e/-a) |
| 8 | Missing grading files | `-e missing-e.txt -a missing-a.txt` | exit 2 | PASS | exit=2; 错误: [Errno 2] No such file or directory: 'missing-a.txt' |
| 9 | Minimum range | `-n 1 -r 1` | one valid exercise | PASS | exit=0; 已生成 1 道题目：C:\Users\Tsubaki\AppData\Local\Temp\pair-arithmetic-io-upte1ps6\Exercises.txt; 1 lines, exact answers, valid numbering, no duplicates |
| 10 | Normal generation | `-n 100 -r 10` | 100 valid exercises and answers | PASS | exit=0; 已生成 100 道题目：C:\Users\Tsubaki\AppData\Local\Temp\pair-arithmetic-io-upte1ps6\Exercises.txt; 100 lines, exact answers, valid numbering, no duplicates |
| 11 | 10,000 generation | `-n 10000 -r 10` | 10,000 valid unique exercises | PASS | exit=0; 已生成 10000 道题目：C:\Users\Tsubaki\AppData\Local\Temp\pair-arithmetic-io-upte1ps6\Exercises.txt; 10000 lines, exact answers, valid numbering, no duplicates |
| 12 | Grading matrix | `-e grade-e.txt -a grade-a.txt` | Correct 1,5; Wrong 2,3,4 | PASS | exit=0; Correct: 2 (1, 5) / Wrong: 3 (2, 3, 4) / 统计结果：C:\Users\Tsubaki\AppData\Local\Temp\pair-arithmetic-io-upte1ps6\Grade.txt; Grade.txt=Correct: 2 (1, 5) / Wrong: 3 (2, 3, 4) |
| 13 | Overwrite outputs | `-n 3 -r 10` | old 10,000-line files replaced by 3 lines | PASS | exit=0; 已生成 3 道题目：C:\Users\Tsubaki\AppData\Local\Temp\pair-arithmetic-io-upte1ps6\Exercises.txt; 3 lines, exact answers, valid numbering, no duplicates |

## 完备性结论

检查覆盖正常输入、最小范围、万人题、缺失参数、非法整数、未知参数、模式冲突、文件缺失、UTF-8 BOM、带分数、正确/错误/缺失/非法答案、重复检测、答案精确性及覆盖写行为。所有生成题均通过重新解析和精确分数求值验证。

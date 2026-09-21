# Pair Arithmetic

小学四则运算题目生成器与答案批改程序。

- 翁佳华（3224004345）
- 廖颖欣（3224004307）
- Python 3.10+，核心程序仅使用标准库

## 运行

在项目根目录执行：

```powershell
python Myapp.py -n 10 -r 10
python Myapp.py -e Exercises.txt -a Answers.txt
python Myapp.py --help
```

生成模式的 `-n`、`-r` 均为必填正整数。题目与答案写入当前目录的 `Exercises.txt`、`Answers.txt`；批改结果写入 `Grade.txt`。所有文件均为 UTF-8。

```text
1. 1/2 + 3 ÷ 4 =
1) 1’1/4
```

输入解析兼容 `+ - * /`、`+ − × ÷` 和直引号形式的带分数。程序使用 `fractions.Fraction` 精确计算，不采用浮点数。

## 约束和判重

- 每题包含1～3个运算符。
- 每个减法子表达式的左值不小于右值。
- 每个除法子表达式的结果严格位于0和1之间。
- `+`、`×` 节点交换左右子树后视为重复，但不会通过结合律任意重组表达式树。
- 达到有限尝试次数仍无法满足数量时明确报错，不会无限循环。

## 测试

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s tests -v
```

当前共19项自动测试，覆盖精确分数、带分数、解析与括号、题面判重示例、生成约束、命令行错误、文件格式、UTF-8 BOM、覆盖写、答案批改和一次生成10000道题。

### 输入输出验收

构建 EXE 后执行真实进程验收：

```powershell
python tools/io_validation.py
```

脚本自动检查帮助信息、非法参数、模式冲突、缺失文件、最小范围、100题、10000题、UTF-8/带分数、批改矩阵和覆盖写，并重新解析全部生成题验证答案与唯一性。当前13个场景全部通过，详见[输入输出验收报告](docs/io-validation.md)。

## 自动性能报告

Pillow 只用于自动输出 PNG 图表：

```powershell
python -m pip install Pillow
powershell -ExecutionPolicy Bypass -File tools/performance.ps1
```

脚本先运行测试，再进行3轮预热和7轮正式万人题测量，自动在 `docs/performance` 生成：

- `results.csv`：原始数据；
- `profile.prof`：可复查的 cProfile 文件；
- `performance-comparison.png`：基线与优化对比；
- `hotspots.png`：热点函数图；
- `report.md`：自动汇总报告。

当前实测优化版平均耗时约814ms，较基线下降49.6%，详见[自动性能报告](docs/performance/report.md)。

## 打包 Windows EXE

```powershell
python -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File tools/build-exe.ps1
dist\Myapp.exe -n 10 -r 10
```

## 目录结构

- `src/arithmetic`：表达式树、生成器、解析器、批改器和 CLI；
- `tests`：19个自动测试；
- `tools`：性能报告和 EXE 打包脚本；
- `samples`：可复现的判题输入样例；
- `docs/blog-final.md`：可直接发布的完整课程博客；
- `docs/local-test-guide.md`：按博客截图编号编排的本机测试指南；
- `docs/blog-draft.md`：早期博客提纲；
- `docs/performance`：真实测试数据、图表和分析文件。

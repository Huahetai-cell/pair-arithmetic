# 本机测试与截图指南

本文按博客中的 S1～S8 截图编号编排。建议将 PowerShell 窗口拉宽到约120列，使用浅色或深色主题均可，但截图中应同时保留“执行命令”和“输出结果”。截图前先关闭包含隐私信息的窗口。

## 0. 准备

打开 PowerShell，进入项目目录：

```powershell
Set-Location D:\pair
git status --short --branch
Test-Path .\dist\Myapp.exe
```

预期 Git 状态显示 `main...origin/main`，EXE 检查显示 `True`。如果 EXE 不存在，需要先安装 Python 3.10+，然后执行：

```powershell
python -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File .\tools\build-exe.ps1
```

## S1：GitHub 与提交历史

浏览器打开 <https://github.com/Huahetai-cell/pair-arithmetic>，进入 Commits 页面。截图应包含仓库名称、公开状态、`main` 分支和多条具有明确说明的提交记录。

## S2：帮助信息和参数说明

```powershell
.\dist\Myapp.exe --help
```

截图应包含两种模式以及 `-n`、`-r`、`-e`、`-a` 四个参数。

## S3：正常生成题目和答案

```powershell
.\dist\Myapp.exe -n 10 -r 10
Get-Content .\Exercises.txt -Encoding UTF8
Get-Content .\Answers.txt -Encoding UTF8
```

建议分成两张截图：第一张显示生成命令和 Exercises.txt，第二张显示 Answers.txt。核对编号从1到10、运算符两侧有空格、题目以 `=` 结尾，答案可能包含自然数、分数或带分数。

## S4：非法输入处理

```powershell
.\dist\Myapp.exe -n 10
.\dist\Myapp.exe -n 0 -r 10
.\dist\Myapp.exe -n abc -r 10
```

截图至少保留第一条命令，画面应显示帮助用法和明确错误信息，证明程序不会静默失败。

## S5：判题功能

仓库已经准备了一组固定输入，其中第1、5题正确，第2题错误，第3题缺失，第4题答案非法：

```powershell
.\dist\Myapp.exe -e .\samples\Exercises-demo.txt -a .\samples\Answers-demo.txt
Get-Content .\Grade.txt -Encoding UTF8
```

预期输出：

```text
Correct: 2 (1, 5)
Wrong: 3 (2, 3, 4)
```

截图需同时包含命令和上述统计结果。

## S6：万人题与自动输入输出验收

先测量万人题运行时间：

```powershell
$elapsed = Measure-Command { .\dist\Myapp.exe -n 10000 -r 10 }
"Exercises=$((Get-Content .\Exercises.txt -Encoding UTF8).Count)"
"Answers=$((Get-Content .\Answers.txt -Encoding UTF8).Count)"
"ElapsedMs=$([math]::Round($elapsed.TotalMilliseconds, 2))"
```

预期题目和答案均为10000行。若电脑已安装 Python，再执行完整黑盒验收：

```powershell
python .\tools\io_validation.py
```

预期显示 `13/13 I/O cases passed`。建议截图这行输出以及万人题行数和耗时。

## S7：自动测试

此步骤需要 Python 3.10+：

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s tests -v
```

预期最后显示：

```text
Ran 19 tests in ...s
OK
```

截取测试列表末尾和汇总行。若 `python` 命令不存在，可尝试 `py`；仍不存在则安装 Python，或者只使用 S2～S6 的 EXE 黑盒测试截图。

## S8：性能分析图

已经生成的两张真实图位于：

- `docs/performance/performance-comparison.png`
- `docs/performance/hotspots.png`

可直接上传到博客。若要在本机重新生成：

```powershell
python -m pip install Pillow
powershell -ExecutionPolicy Bypass -File .\tools\performance.ps1
```

脚本会先跑测试，再完成3轮预热、7轮正式万人题测试，并覆盖生成 CSV、cProfile 和两张 PNG。

## 发布前检查

- 将博客中所有 `【需截图 Sx】` 替换成实际上传后的图片。
- 填写 PSP 实际时间，并重新计算合计。
- 两位成员分别补充真实的结对感受、对方闪光点和建议。
- 不要在截图中显示 GitHub 令牌、邮箱密码或其他隐私信息。
- 保留 `docs/io-validation.md` 和 `docs/performance/report.md` 作为可复查证据。


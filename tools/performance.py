from __future__ import annotations

import cProfile
import csv
import os
import pstats
import statistics
import sys
import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from arithmetic.generator import ExerciseGenerator  # noqa: E402
from arithmetic.parser import ExpressionParser  # noqa: E402

COUNT = 10_000
VALUE_RANGE = 10
WARMUPS = 3
RUNS = 7
OUTPUT = ROOT / "docs" / "performance"


@dataclass(frozen=True, slots=True)
class Measurement:
    strategy: str
    run: int
    elapsed_ms: float
    throughput: float
    peak_bytes: int
    candidates: int
    constraint_rejects: int
    duplicates: int


def baseline_key(expression) -> str:
    """Simulate the original uncached design by rebuilding the key from rendered text."""
    return ExpressionParser().parse(expression.render()).canonical_key


def optimized_key(expression) -> str:
    return expression.canonical_key


def measure(strategy: str, run: int, seed: int, key_strategy) -> Measurement:
    tracemalloc.start()
    started = time.perf_counter_ns()
    result = ExerciseGenerator().generate(COUNT, VALUE_RANGE, seed, key_strategy)
    elapsed_seconds = (time.perf_counter_ns() - started) / 1_000_000_000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return Measurement(
        strategy,
        run,
        elapsed_seconds * 1000,
        COUNT / elapsed_seconds,
        peak,
        result.stats.candidates,
        result.stats.constraint_rejects,
        result.stats.duplicates,
    )


def run_benchmark() -> list[Measurement]:
    for index in range(WARMUPS):
        measure("baseline-warmup", index + 1, 7000 + index, baseline_key)
        measure("optimized-warmup", index + 1, 7000 + index, optimized_key)
    values: list[Measurement] = []
    for index in range(1, RUNS + 1):
        seed = 20_260_900 + index
        values.append(measure("baseline", index, seed, baseline_key))
        values.append(measure("optimized", index, seed, optimized_key))
    return values


def profile_optimized() -> list[tuple[str, int, float]]:
    profile_path = OUTPUT / "profile.prof"
    profiler = cProfile.Profile()
    profiler.enable()
    for index in range(3):
        ExerciseGenerator().generate(COUNT, VALUE_RANGE, 800_000 + index, optimized_key)
    profiler.disable()
    profiler.dump_stats(profile_path)
    stats = pstats.Stats(profiler)
    rows: list[tuple[str, int, float]] = []
    for (filename, line, function), data in stats.stats.items():
        primitive_calls, total_calls, total_time, cumulative_time, _ = data
        if "arithmetic" in filename or "performance.py" in filename:
            rows.append((f"{Path(filename).name}:{line} {function}", total_calls, cumulative_time))
    return sorted(rows, key=lambda row: row[2], reverse=True)[:10]


def write_csv(values: list[Measurement]) -> None:
    with (OUTPUT / "results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(Measurement.__dataclass_fields__.keys())
        for value in values:
            writer.writerow((value.strategy, value.run, f"{value.elapsed_ms:.3f}", f"{value.throughput:.3f}",
                             value.peak_bytes, value.candidates, value.constraint_rejects, value.duplicates))


def summary(values: list[Measurement], strategy: str) -> dict[str, float]:
    selected = [value for value in values if value.strategy == strategy]
    elapsed = sorted(value.elapsed_ms for value in selected)
    throughput = [value.throughput for value in selected]
    p95_index = max(0, min(len(elapsed) - 1, int(len(elapsed) * 0.95 + 0.999) - 1))
    return {
        "mean": statistics.fmean(elapsed),
        "median": statistics.median(elapsed),
        "p95": elapsed[p95_index],
        "throughput": statistics.fmean(throughput),
        "memory": max(value.peak_bytes for value in selected) / 1024 / 1024,
    }


def font(size: int, bold: bool = False):
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def chart_canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1400, 800), "#f8fafc")
    draw = ImageDraw.Draw(image)
    draw.text((60, 40), title, fill="#0f172a", font=font(34, True))
    return image, draw


def draw_pair(draw, box, title: str, baseline: float, optimized: float, lower_better: bool) -> None:
    x, y, width, height = box
    draw.text((x, y), title, fill="#0f172a", font=font(20, True))
    maximum = max(baseline, optimized, 0.0001) * 1.15
    chart_top, chart_bottom = y + 45, y + height - 55
    available = chart_bottom - chart_top
    for value, offset, color, label in (
        (baseline, 65, "#94a3b8", "Baseline"),
        (optimized, 285, "#0ea5e9", "Optimized"),
    ):
        bar_height = max(2, int(value / maximum * available))
        draw.rounded_rectangle((x + offset, chart_bottom - bar_height, x + offset + 145, chart_bottom), 12, fill=color)
        draw.text((x + offset + 20, chart_bottom - bar_height - 27), f"{value:.2f}", fill="#0f172a", font=font(16))
        draw.text((x + offset + 25, chart_bottom + 8), label, fill="#0f172a", font=font(16))
    change = (optimized / baseline - 1) * 100
    direction = "lower is better" if lower_better else "higher is better"
    draw.text((x + 90, y + height - 22), f"Change {change:+.1f}% ({direction})", fill="#334155", font=font(15))


def draw_comparison(values: list[Measurement]) -> None:
    baseline, optimized = summary(values, "baseline"), summary(values, "optimized")
    image, draw = chart_canvas("10,000 Exercise Performance: Baseline vs Optimized")
    draw_pair(draw, (70, 130, 560, 280), "Mean elapsed time (ms)", baseline["mean"], optimized["mean"], True)
    draw_pair(draw, (760, 130, 560, 280), "Throughput (exercises/s)", baseline["throughput"], optimized["throughput"], False)
    draw_pair(draw, (70, 460, 560, 260), "P95 elapsed time (ms)", baseline["p95"], optimized["p95"], True)
    draw_pair(draw, (760, 460, 560, 260), "Peak traced memory (MiB)", baseline["memory"], optimized["memory"], True)
    image.save(OUTPUT / "performance-comparison.png")


def draw_hotspots(hotspots: list[tuple[str, int, float]]) -> None:
    image, draw = chart_canvas("cProfile Hotspots (Optimized Generator)")
    maximum = max((row[2] for row in hotspots), default=1)
    y = 115
    for name, calls, cumulative in hotspots:
        label = name if len(name) <= 47 else name[:44] + "..."
        draw.text((55, y + 9), label, fill="#0f172a", font=font(15))
        width = max(2, int(cumulative / maximum * 720))
        draw.rounded_rectangle((520, y, 520 + width, y + 34), 8, fill="#f97316")
        draw.text((535 + width, y + 8), f"{cumulative:.3f}s / {calls} calls", fill="#0f172a", font=font(14))
        y += 62
    image.save(OUTPUT / "hotspots.png")


def write_report(values: list[Measurement], hotspots: list[tuple[str, int, float]]) -> None:
    baseline, optimized = summary(values, "baseline"), summary(values, "optimized")
    rows = []
    for label, data in (("Baseline", baseline), ("Optimized", optimized)):
        rows.append(f"| {label} | {data['mean']:.2f} | {data['median']:.2f} | {data['p95']:.2f} | "
                    f"{data['throughput']:.2f} | {data['memory']:.2f} |")
    hotspot_rows = "\n".join(f"| `{name}` | {calls} | {cumulative:.3f} |" for name, calls, cumulative in hotspots)
    report = f"""# 自动性能分析报告

- Python：{sys.version.split()[0]}
- 系统：{sys.platform}
- 测试负载：每轮 10000 题、范围 10、3 轮预热、7 轮正式测试
- 公平性：两种策略每轮使用相同随机种子；基线从格式化文本重新解析判重结构，优化版读取表达式节点缓存的判重键。

| 策略 | 平均耗时(ms) | 中位数(ms) | P95(ms) | 平均吞吐量(题/秒) | 峰值跟踪内存(MiB) |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

优化版平均耗时变化为 **{(optimized['mean'] / baseline['mean'] - 1) * 100:+.1f}%**，吞吐量变化为 **{(optimized['throughput'] / baseline['throughput'] - 1) * 100:+.1f}%**。

![性能对比](performance-comparison.png)

## cProfile 热点

| 函数 | 调用次数 | 累计时间(s) |
|---|---:|---:|
{hotspot_rows}

![热点函数](hotspots.png)

原始数据见 [results.csv](results.csv)，完整分析文件为 `profile.prof`，可用 `python -m pstats profile.prof` 复查。
"""
    (OUTPUT / "report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    values = run_benchmark()
    hotspots = profile_optimized()
    write_csv(values)
    draw_comparison(values)
    draw_hotspots(hotspots)
    write_report(values, hotspots)
    print(f"Performance report generated at {OUTPUT}")


if __name__ == "__main__":
    main()


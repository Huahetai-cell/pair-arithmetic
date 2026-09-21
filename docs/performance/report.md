# 自动性能分析报告

- Python：3.12.14
- 系统：win32
- 测试负载：每轮 10000 题、范围 10、3 轮预热、7 轮正式测试
- 公平性：两种策略每轮使用相同随机种子；基线从格式化文本重新解析判重结构，优化版读取表达式节点缓存的判重键。

| 策略 | 平均耗时(ms) | 中位数(ms) | P95(ms) | 平均吞吐量(题/秒) | 峰值跟踪内存(MiB) |
|---|---:|---:|---:|---:|---:|
| Baseline | 1614.77 | 1570.02 | 1850.89 | 6225.30 | 9.98 |
| Optimized | 814.00 | 812.88 | 926.84 | 12340.02 | 9.24 |

优化版平均耗时变化为 **-49.6%**，吞吐量变化为 **+98.2%**。

![性能对比](performance-comparison.png)

## cProfile 热点

| 函数 | 调用次数 | 累计时间(s) |
|---|---:|---:|
| `generator.py:25 generate` | 3 | 3.806 |
| `generator.py:60 _build` | 327913 | 3.551 |
| `generator.py:87 _atom` | 196739 | 1.906 |
| `expression.py:72 __post_init__` | 196739 | 0.580 |
| `expression.py:91 __post_init__` | 82657 | 0.408 |
| `expression.py:51 commutative` | 82657 | 0.017 |
| `performance.py:46 optimized_key` | 37000 | 0.004 |

![热点函数](hotspots.png)

原始数据见 [results.csv](results.csv)，完整分析文件为 `profile.prof`，可用 `python -m pstats profile.prof` 复查。
